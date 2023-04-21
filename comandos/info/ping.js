module.exports = {
    name: "ping",
    aliases: ["latencia", "ms"],
    desc: "Sirve para ver la latencia del bot",
    run: async (client, message, args, prefix) => {
        message.reply(`Pong! El ping del Bot es de ${client.ws.ping}ms`)
    }
}