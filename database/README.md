# LuminaLearn AI — Database Governance & Schema Architecture

## Overview
LuminaLearn AI utilizes **PostgreSQL 16** as its core relational data store for persistent user data, Bayesian knowledge graphs, mastery tracking, and interaction telemetry.

## Directory Structure
- `schema.sql`: Master PostgreSQL DDL script defining enums, tables, keys, and indexes.
- `init/`: Docker initialization SQL scripts for setting up local development DB containers.
- `seeds/`: Initial seed data scripts for populating default knowledge graph nodes.

## Migration Tooling
Database schema migrations are managed asynchronously via **Alembic** located in `backend/app/db/migrations/`.
