# ARC editor

External ARC problem editor / viewer under `external/arc-app`. The Express API talks to a shared MongoDB Atlas database.

## Installation

1. Install [Node.js](https://nodejs.org/) if needed.
2. From this directory (`external/arc-app`), install server deps:

   ```bash
   npm install
   ```

3. Install client deps:

   ```bash
   cd client && npm install && cd ..
   ```

## MongoDB credentials (`MONGODB_URI`)

The server **no longer hardcodes** the database password. Set `MONGODB_URI` in a local `.env` file (gitignored):

```bash
cp .env.example .env
```

Then edit `.env` and set:

```bash
MONGODB_URI=mongodb+srv://USER:PASSWORD@HOST/DB?retryWrites=true&w=majority
PORT=3001
```

Ask a teammate or the project lead for the shared Atlas URI (the same one previously embedded in `server/index.js`). **Do not commit `.env`.**

Without `MONGODB_URI`, `npm start` exits with an error.

## To run

**Client only** (no DB):

```bash
cd client && npm start
```

**Client + API** (needed for database-backed categories/problems):

```bash
# from external/arc-app
npm run build
npm start
```

The API listens on `PORT` (default `3001`).
