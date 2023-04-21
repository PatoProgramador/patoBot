const fs = require('fs');

module.exports = (client) => {
    try {
        let commandos = 0;
        fs.readdirSync("./comandos/").forEach((folder) => {
            const commands = fs.readdirSync(`./comandos/${folder}`).filter((file) => file.endsWith(".js"))
            for(let archivo of commands) {
                let command = require(`../comandos/${folder}/${archivo}`);
                if(command.name) {
                    client.commands.set(command.name, command)
                    commandos++
                } else {
                    console.log(`COMANDO [/${folder}/${file}]`, 'error => el comando no está configurado')
                    continue;
                }
                if(command.aliases && Array.isArray(command.aliases)) command.aliases.forEach((alias) => client.set(alias, command.name))
            }
        });
        console.log(`${commandos} Comandos cargados`)
    } catch (error) {
        console.log(error)
    }
};