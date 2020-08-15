
import telebot # pip install pyTelegramBotAPI
import redis # pip install redis

bot = telebot.TeleBot("858391547:AAFImuQo1uxmdI-lr8uECU6y3yVzeEhW_SA")

r = redis.Redis(
    host='ec2-54-165-127-148.compute-1.amazonaws.com',
    port=11899, 
    password='pdc4f8b8835bfbdf05d01824fc167ab9b14e72b5548221ffb58014536416710ab'
)

# r = redis.Redis(
#     host='127.0.0.1',
#     port=6379, 
# )


bot.state = None # create own value `.state` in `bot` - so I don't have to use `global state`. Similar way I could create and use `bot.data`

CRIAR = 1
TAREFAS = 2
DONE = 3

# it has to be before functions which check `bot.state`
@bot.message_handler(commands=['cancel'])
def test(message):
    bot.send_message(message.chat.id, 'canceled')
    bot.state = None

@bot.message_handler(commands=['criar'])
def criar(message):
    bot.send_message(message.chat.id, 'Por favor digite sua tarefa:')
    bot.state = CRIAR


@bot.message_handler(func=lambda msg:bot.state==CRIAR)
def criar_tarefa(message):
    chat_id = message.chat.id
    teste = r.hgetall(chat_id)
    r.hset(chat_id, message.text,'a')

    bot.send_message(message.chat.id,'Tarefa criada com sucesso!')
    bot.state = None


@bot.message_handler(commands=['tarefas'])
def listar_tarefas(message):
    chat_id = message.chat.id # id do usuario
    teste = r.hgetall(chat_id) # lista de tarefas 
    ind= {k:i for i,k in enumerate(teste.keys())} #indice
    lista = ""
    if not teste:
        lista = "Voce ainda não possui tarefas."
    else: 
        lista = "Lista de Tarefas: \n\n"
        for key, value in teste.items():
            if(value.decode('utf-8') == 'a'):
                lista = lista + str(ind[key] + 1) + ' ' + key.decode('utf-8') + '\n'
            else:
                lista = lista + str(ind[key] + 1) + ' ' + key.decode('utf-8') + " ✔" + '\n'

    bot.send_message(message.chat.id, lista)   
    bot.state = None

@bot.message_handler(commands=['done'])
def done(message):
    listar_tarefas(message)
    bot.send_message(message.chat.id, 'Por favor digite o numero da tarefa finalizada:')
    bot.state = DONE

@bot.message_handler(func=lambda msg:bot.state==DONE)
def marcar_inativo(message):
    chat_id = message.chat.id # id do usuario
    identificador = int(message.text)
    listaTarefas = list(r.hgetall(chat_id)) # lista de tarefas 
    tam = len(listaTarefas)
    if(identificador > 0 and identificador <= tam):
        field = listaTarefas[identificador - 1]
        r.hset(chat_id, field,'i')
    bot.state = None    


@bot.message_handler(commands=['apagar'])
def apagar_inativo(message):
    chat_id = message.chat.id # id do usuario
    teste = r.hgetall(chat_id) # lista de tarefas 

    if not teste:
        lista = "Voce ainda não possui tarefas."
    else: 
        for key, value in teste.items():
            if(value.decode('utf-8') == 'i'):
                r.hdel(chat_id,key)
    bot.state = None
        
bot.polling()


