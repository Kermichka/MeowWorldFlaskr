const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('flaskr.sqlite');
const query = 'SELECT * FROM products';

db.all(query, [], (err, rows) => {
  if (err) {
    throw err;
  }

  // Process the fetched data (rows) here
  console.log(rows);

  // Close the database connection
  db.close((err) => {
    if (err) {
      console.error('Error closing the database:', err.message);
    } else {
      console.log('Database connection closed.');
    }
  });
});