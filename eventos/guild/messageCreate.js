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

    // Buscar el comando en la colección de comandos
    const args = message.content.slice(data.prefijo.length).trim().split(/ +/);
    // const args = message.content.slice(data.prefijo.length).trim().split(" ");
    const commandName = args.shift()?.toLowerCase();
    const command = client.commands.find(cmd => cmd.name == commandName) || client.commands.find(cmd => cmd.aliases && cmd.aliases.includes(commandName))

    let cmdFunction;

    if (command && typeof command == "object") {
      cmdFunction = command.run;
    } else {
      // Si el comando no existe, mostrar un mensaje de error
      return message.reply(`El comando "${commandName}" no existe. Por favor, use \`${data.prefijo}help\` para ver una lista de comandos disponibles.`);
    }
    
    // Ejecutar el comando
    try {
      await cmdFunction(client, message, args, data.prefijo);
    } catch (error) {
      console.error(error);
      message.reply('¡Ups! Ha ocurrido un error al ejecutar este comando.');
    }
};