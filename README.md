# Bookstore Simulator with Optimization

A comprehensive bookstore simulation system with multiple optimization approaches for inventory management.

## Architecture

### Components

1. **Simulator Core** (`/simulator`)
   - Main simulation engine
   - Supports multiple solver backends
   - Handles inventory, customers, and sales tracking

2. **Timefold Optimizer** (`/timefold_bookstore`)
   - Web API based optimization service
   - Constraint-based solver
   - RESTful interface for optimization requests

3. **Alternative Solver** (`/simulator/alt_solver`)
   - Standalone Late Acceptance Hill Climbing implementation
   - Direct Python implementation for comparison

## Setup

### Prerequisites
- Python 3.11+
- JDK 17+ (for Timefold)
- pip and venv

### Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install simulator
cd simulator
pip install -e .

# Install Timefold component
cd ../timefold_bookstore
pip install -e .

to start timefold server see timefold_bookstore/README.adoc