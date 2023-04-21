const mongoose = require('mongoose');
require('dotenv').config();

module.exports = client => {
    mongoose.connect(process.env.MONGO_DB_URI)
}