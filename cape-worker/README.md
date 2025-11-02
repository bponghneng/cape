# Cape Worker

A standalone daemon that continuously polls the cape_issues database table for pending issues and executes the appropriate workflows using the cape-adw command. The worker operates independently of the CLI, providing automated background processing of issues with proper locking mechanisms to prevent race conditions between multiple worker instances.

## Features

- **Automated Issue Processing**: Continuously monitors and processes pending issues from the database
- **Distributed Worker Support**: Multiple worker instances can run simultaneously without conflicts
- **Robust Error Handling**: Automatically retries failed issues and handles timeouts gracefully
- **Configurable Polling**: Customizable poll intervals and logging levels
- **System Integration**: Includes systemd (Linux) and launchd (macOS) configurations
- **Comprehensive Logging**: File and console logging with rotation support

## Installation

### Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- PostgreSQL database with cape_issues table
- Environment variables configured (see `.env` file)

### Quick Install

Use the provided installation script to set up the worker as a system service:

```bash
# From the cape directory
./cape-worker/scripts/install-worker.sh <worker-id>

# Example
./cape-worker/scripts/install-worker.sh alleycat-1
```

The script will:
- Verify all dependencies are installed
- Create necessary log directories
- Configure the worker as a system service (systemd or launchd)
- Start the worker automatically

### Manual Installation

If you prefer to run the worker manually without system integration:

```bash
# From the cape directory
python -m cape-worker --worker-id <worker-id> [OPTIONS]
```

## Usage

### Command Line Arguments

```
python -m cape-worker --worker-id <worker-id> [OPTIONS]

Required Arguments:
  --worker-id TEXT          Unique identifier for this worker instance
                           (e.g., 'alleycat-1', 'tyderium-1')

Optional Arguments:
  --poll-interval INTEGER  Number of seconds to wait between polls
                           (default: 10)
  --log-level LEVEL       Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
                           (default: INFO)
```

### Examples

Basic usage with default settings:
```bash
python -m cape-worker --worker-id alleycat-1
```

Custom poll interval and debug logging:
```bash
python -m cape-worker --worker-id tyderium-1 --poll-interval 5 --log-level DEBUG
```

### Managing the Worker Service

#### macOS (launchd)

```bash
# Start the worker
launchctl start com.cape.worker.<worker-id>

# Stop the worker
launchctl stop com.cape.worker.<worker-id>

# Restart the worker
launchctl stop com.cape.worker.<worker-id> && launchctl start com.cape.worker.<worker-id>

# Check status
launchctl list | grep com.cape.worker.<worker-id>

# Unload the service
launchctl unload ~/Library/LaunchAgents/com.cape.worker.<worker-id>.plist
```

#### Linux (systemd)

```bash
# Start the worker
sudo systemctl start cape-worker-<worker-id>.service

# Stop the worker
sudo systemctl stop cape-worker-<worker-id>.service

# Restart the worker
sudo systemctl restart cape-worker-<worker-id>.service

# Check status
sudo systemctl status cape-worker-<worker-id>.service

# View logs
sudo journalctl -u cape-worker-<worker-id>.service -f

# Disable the service
sudo systemctl disable cape-worker-<worker-id>.service
```

## Architecture

The worker is organized as a modular Python package:

```
cape-worker/
├── __init__.py          # Package initialization with exports
├── __main__.py          # Module entry point for python -m execution
├── worker.py            # Core IssueWorker class
├── database.py          # Database operations and queries
├── config.py            # Configuration management
├── cli.py               # Command-line interface
├── tests/               # Unit tests
├── migrations/          # Database migrations
├── scripts/             # Installation and utility scripts
├── daemons/             # System service configurations
└── logs/                # Log files directory
```

### Key Components

- **IssueWorker**: Main worker class that handles the polling loop and workflow execution
- **WorkerConfig**: Configuration dataclass with validation
- **Database Module**: Functions for retrieving and updating issues
- **CLI Module**: Command-line argument parsing and worker initialization

## Database Schema

The worker interacts with the `cape_issues` table:

```sql
CREATE TABLE cape_issues (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    assigned_worker_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

Status values:
- `pending`: Issue is waiting to be processed
- `started`: Issue is currently being processed
- `completed`: Issue has been successfully processed

## Logging

Logs are written to the `logs/` directory with the following files:

- `worker_<worker-id>.log`: Application-level logs
- `worker_<worker-id>_stdout.log`: Standard output from the worker process
- `worker_<worker-id>_stderr.log`: Standard error from the worker process

Log format:
```
YYYY-MM-DD HH:MM:SS - cape_worker_<worker-id> - LEVEL - Message
```

## Development

### Running Tests

```bash
# Run all tests
cd cape && python -m pytest cape-worker/tests/ -v

# Run with coverage
cd cape && python -m pytest cape-worker/tests/ -v --cov=cape-worker

# Run specific test file
cd cape && python -m pytest cape-worker/tests/test_worker.py -v
```

### Project Structure

The cape-worker package follows standard Python package conventions:

- Each module has a single, well-defined responsibility
- Imports use relative imports within the package
- Configuration is centralized in `config.py`
- Database operations are isolated in `database.py`
- CLI logic is separated from core worker logic

## Troubleshooting

### Worker Not Starting

1. Check that all dependencies are installed:
   ```bash
   python3 --version
   uv --version
   ```

2. Verify environment variables are set:
   ```bash
   # Check .env file exists
   cat .env
   ```

3. Check log files for errors:
   ```bash
   tail -f logs/worker_<worker-id>.log
   ```

### Issues Not Being Processed

1. Verify the worker is running:
   ```bash
   # macOS
   launchctl list | grep com.cape.worker

   # Linux
   sudo systemctl status cape-worker-<worker-id>
   ```

2. Check for database connectivity:
   ```bash
   # Test database connection
   python -c "from cape_worker.database import get_client; print(get_client())"
   ```

3. Verify issues exist in the database:
   ```sql
   SELECT * FROM cape_issues WHERE status = 'pending';
   ```

### Worker Crashes or Timeouts

1. Check workflow timeout settings (default: 3600 seconds)
2. Review error logs in `logs/worker_<worker-id>_stderr.log`
3. Increase logging level to DEBUG for more details
4. Verify sufficient system resources (memory, disk space)

## Contributing

When contributing to the cape-worker package:

1. Add tests for new functionality in `tests/`
2. Update this README if adding new features
3. Follow the existing code structure and conventions
4. Ensure all tests pass before submitting changes

## License

[Add license information here]
