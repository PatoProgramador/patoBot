const mongoose = require('mongoose');
require('dotenv').config();

module.exports = client => {
    // conexion con la base de datos
    mongoose.connect(process.env.MONGO_DB_URI, {
        useNewUrlParser: true,
        useUnifiedTopology: true
    }).then(() => {
        console.log('Conectado a la base de datos de MongoDB')
    }).catch((err) => {
        console.log('Error al conectar a la base de datos de MongoDB')
        console.log(err)
    })
    // estado de conexion del bot
    console.log(`Conectado como ${client.user.tag}`)
}