const Discord  = require('discord.js');
require('dotenv').config();
const client = new Discord.Client({ intents: [131071]});

client.commands = new Discord.Collection();
client.aliases = new Discord.Collection();

function requestHandlers() {
    ["command", "events", "distube"].forEach(handler => {
        try {
            require(`./handlers/${handler}`)(client, Discord)
        } catch (error) {
            console.warn(error)
        }
    })
}
requestHandlers();

client
    .login(process.env.DS_BOT_TOKEN)
    .then(() => {
        client.user.setActivity('existir');
    })
    .catch((err) => console.log(err));
