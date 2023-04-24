require('dotenv').config();
const serverSchema = require('../../models/servidor');
const { asegurar } = require('../../handlers/functions');

module.exports = async (client, message) => {
    if (!message.guild || !message.channel || message.author.bot) return;
    let data = await asegurar(serverSchema, "guildID", message.guild.id, {
        guildID: message.guild.id,
        prefijo: process.env.PREFIX
    });
    if (!message.content.startsWith(data.prefijo) || message.author.bot) return;

    // Dividimos el mensaje en un array y tomamos el primer elemento como el comando.
    const args = message.content.slice(data.prefijo.length).trim().split(/ +/);
    const commandName = args.shift().toLowerCase();
  
    // Buscamos el comando en la colección de comandos del bot.
    const command = client.commands.get(commandName);
  
    // Si el comando no existe, enviamos un mensaje indicando que no se reconoce el comando.
    if (!command) {
      return message.reply(`El comando ${commandName} no existe. Intenta con ${data.prefijo}help para ver la lista de comandos.`);
    }
  
    try {
      // Ejecutamos el comando y manejamos cualquier posible error.
      await command.execute(client, message, args);
    } catch (error) {
      console.error(error);
      message.reply('¡Ups! Ha ocurrido un error al ejecutar este comando.');
    }
    // if (!message.content.startsWith(data.prefijo)) return;
    // const args = message.content.slice(data.prefijo.length).trim().split(" ");
    // const cmd = args.shift()?.toLowerCase();
    // const command = client.commands.get(cmd) || client.commands.find(c => c.aliases && c.alises.includes(cmd))
    // if (command) {
    //     command.run(client, message, args, data.prefijo)
    // } else {
    //     return message.reply("No he encontrado el comando especificado")
    // }
};