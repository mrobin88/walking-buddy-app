#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to get computer's IP address
get_ip() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        ipconfig | grep "IPv4 Address" | head -1 | awk '{print $NF}'
    else
        # Linux/Mac
        hostname -I | awk '{print $1}'
    fi
}

# Function to update docker-compose.yml with current IP
update_ip() {
    local ip=$(get_ip)
    echo -e "${BLUE}Updating docker-compose.yml with IP: $ip${NC}"
    
    # Update docker-compose.yml
    sed -i.bak "s/your-computer-ip/$ip/g" docker-compose.yml
    sed -i.bak "s/your-computer-ip/$ip/g" nginx.conf
    
    echo -e "${GREEN}Updated configuration with IP: $ip${NC}"
}

# Function to start services
start() {
    echo -e "${BLUE}Starting Walking Buddy application...${NC}"
    update_ip
    docker-compose up -d
    echo -e "${GREEN}Application started!${NC}"
    echo -e "${YELLOW}Access your app at: http://$(get_ip)${NC}"
    echo -e "${YELLOW}Admin interface: http://$(get_ip)/admin/${NC}"
    echo -e "${YELLOW}Username: admin, Password: admin123${NC}"
}

# Function to stop services
stop() {
    echo -e "${BLUE}Stopping Walking Buddy application...${NC}"
    docker-compose down
    echo -e "${GREEN}Application stopped!${NC}"
}

# Function to restart services
restart() {
    echo -e "${BLUE}Restarting Walking Buddy application...${NC}"
    docker-compose down
    docker-compose up -d
    echo -e "${GREEN}Application restarted!${NC}"
    echo -e "${YELLOW}Access your app at: http://$(get_ip)${NC}"
}

# Function to show logs
logs() {
    echo -e "${BLUE}Showing logs...${NC}"
    docker-compose logs -f
}

# Function to show status
status() {
    echo -e "${BLUE}Container status:${NC}"
    docker-compose ps
    echo -e "${BLUE}Access URLs:${NC}"
    echo -e "${YELLOW}Main app: http://$(get_ip)${NC}"
    echo -e "${YELLOW}Admin: http://$(get_ip)/admin/${NC}"
    echo -e "${YELLOW}Health check: http://$(get_ip)/health/${NC}"
}

# Function to backup database
backup() {
    echo -e "${BLUE}Creating database backup...${NC}"
    docker-compose exec db pg_dump -U postgres walking_buddy_db > backup_$(date +%Y%m%d_%H%M%S).sql
    echo -e "${GREEN}Backup created!${NC}"
}

# Function to restore database
restore() {
    if [ -z "$1" ]; then
        echo -e "${RED}Please specify backup file: ./manage-docker.sh restore backup_file.sql${NC}"
        exit 1
    fi
    echo -e "${BLUE}Restoring database from $1...${NC}"
    docker-compose exec -T db psql -U postgres walking_buddy_db < "$1"
    echo -e "${GREEN}Database restored!${NC}"
}

# Function to show help
help() {
    echo -e "${BLUE}Walking Buddy Docker Management Script${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the application"
    echo "  stop      - Stop the application"
    echo "  restart   - Restart the application"
    echo "  logs      - Show application logs"
    echo "  status    - Show container status and URLs"
    echo "  backup    - Create database backup"
    echo "  restore   - Restore database from backup file"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs"
    echo "  $0 backup"
    echo "  $0 restore backup_20241210_143022.sql"
}

# Main script logic
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    help|--help|-h)
        help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac 