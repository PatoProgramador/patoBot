const fs = require('fs');

const allEvents = [];

module.exports = async (client) => {
    try {
        try {
            console.log('Cargando los eventos...')
        } catch {}
        let cantidad = 0;
        const cargar_dir = (dir) => {
            const archivos_eventos = fs.readdirSync(`./eventos/${dir}`).filter((file) => file.endsWith('.js'));
            for(const archivo of archivos_eventos) {
                try {
                   const evento = require(`../eventos/${dir}/${archivo}`) 
                   const nombre_evento = archivo.split(".")[0];
                   allEvents.push(nombre_evento);
                   client.on(nombre_evento, evento.bind(null, client));
                   cantidad++
                } catch (error) {
                    console.log(error)
                }
            }
        }
        await ["client", "guild"].forEach(e => cargar_dir(e))
        console.log(`${cantidad} Eventos cargados`)
        try {
            console.log("Iniciando sesión del Bot...")
        } catch (error) {
            console.log(error)
        }
    } catch (error) {
        console.log(error)
    }
};