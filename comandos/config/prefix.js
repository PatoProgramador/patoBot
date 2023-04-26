const schema = require('../../models/servidor');

module.exports  = {
    name: "prefix",
    aliases: ["prefijo", "cambiarprefijo", "cambiarprefix"],
    desc: "Sirve para cambiar el Prefijo del Bot en el servidor",
    run: async (client, message, args, prefix) => {
        if(!args[0]) return message.reply('Tienes que especificar el nuevo prefijo :)');
        await schema.findOneAndUpdate({guildID: message.guild.id}, {
            prefijo: args[0]
        })
        return message.reply(`He cambiado el prefijo de /${prefix}/ a /${args[0]}/`)
    }
}