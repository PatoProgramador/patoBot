module.exports = {
    asegurar,
};

async function asegurar(schema, id, id2, object) {
    let data = await schema.findOne({ guildID: id2 });
    if (!data) {
        console.log('No hay base de datos creada, creando una...')
        data = await new schema(object);
        await data.save();
    }
    return data;
};