const express = require('express');
const exphbs = require('express-handlebars');
const path = require('path');
const morgan = require('morgan');
const helmet = require('helmet');
const compression = require('compression');
const sqlite3 = require('sqlite3').verbose();

const app = express();

// Set up SQLite database
const dbPath = path.join('C:', 'Users', 'ADMIN', 'Downloads', 'vision_x_studios', 'vision_x_studios', 'users.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database', err);
    } else {
        console.log('Connected to the SQLite database.');
    }
});

// Set up Handlebars as the template engine with a default layout
app.engine('handlebars', exphbs({
    defaultLayout: 'main',
    layoutsDir: path.join(__dirname, 'views/layouts')
}));
app.set('view engine', 'handlebars');

// Set the directory for the views
app.set('views', path.join(__dirname, 'views'));

// Middleware
app.use(helmet()); // Adds various HTTP headers for security
app.use(morgan('dev')); // Logging middleware
app.use(express.json()); // Parse JSON request bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded request bodies
app.use(compression()); // Compress all routes

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.get('/', (req, res) => {
    res.render('home', { title: 'Home' });
});

// Example route using the database
app.get('/users', (req, res) => {
    db.all("SELECT * FROM users", [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ users: rows });
    });
});

// 404 handler
app.use((req, res, next) => {
    res.status(404).render('404', { title: '404: Page Not Found' });
});

// Error handler
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).render('500', { title: '500: Internal Server Error' });
});

// Graceful shutdown
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error(err.message);
        }
        console.log('Closed the database connection.');
        process.exit(0);
    });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
