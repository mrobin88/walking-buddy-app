const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const router = express.Router();

// Webhook handler
router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];

    let event;

    try {
        event = stripe.webhooks.constructEvent(
            req.body,
            sig,
            process.env.STRIPE_WEBHOOK_SECRET
        );
    } catch (err) {
        console.log('⚠️  Webhook signature verification failed:', err.message);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Handle the event
    switch (event.type) {
        case 'checkout.session.completed':
            const session = event.data.object;
            
            // Update user's subscription status
            const userId = session.metadata.user_id;
            
            try {
                const user = await User.findById(userId);
                if (!user) {
                    console.log('⚠️  User not found:', userId);
                    break;
                }

                user.subscription_plan = 'premium';
                user.subscription_expiry = new Date(session.subscription.current_period_end * 1000);
                user.is_premium = true;
                
                // Create or update profile
                let profile = await Profile.findOne({ user: userId });
                if (!profile) {
                    profile = new Profile({ user: userId });
                }
                profile.stripe_customer_id = session.customer;
                profile.subscription_expires = user.subscription_expiry;
                
                await Promise.all([
                    user.save(),
                    profile.save()
                ]);

                console.log('✅ User upgraded to premium:', userId);
            } catch (err) {
                console.error('❌ Error updating user subscription:', err);
            }
            break;

        case 'invoice.payment_succeeded':
            const invoice = event.data.object;
            
            try {
                const user = await User.findById(invoice.metadata.user_id);
                if (!user) break;

                // Update subscription expiry
                user.subscription_expiry = new Date(invoice.period_end * 1000);
                await user.save();

                console.log('✅ Subscription renewed:', invoice.metadata.user_id);
            } catch (err) {
                console.error('❌ Error updating subscription:', err);
            }
            break;

        case 'customer.subscription.deleted':
            const subscription = event.data.object;
            
            try {
                const user = await User.findById(subscription.metadata.user_id);
                if (!user) break;

                user.subscription_plan = 'basic';
                user.subscription_expiry = null;
                user.is_premium = false;
                await user.save();

                console.log('✅ Subscription cancelled:', subscription.metadata.user_id);
            } catch (err) {
                console.error('❌ Error cancelling subscription:', err);
            }
            break;

        default:
            console.log(`ℹ️  Unhandled event type: ${event.type}`);
    }

    res.json({ received: true });
});

module.exports = router;
