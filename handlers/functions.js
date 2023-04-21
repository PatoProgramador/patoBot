module.exports = {
    asegurar,
};

async function asegurar(schema, id, id2, object){
    const data = await schema.findOne({id: id2});
    if(!data){
        console.log('No hay base de datos creada, creando una...')
        data = await new schema(object).then(async data  => await data.save())
    }
    return data;
};