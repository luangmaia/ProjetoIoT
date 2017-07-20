import tweepy, datetime, time, json, paho.mqtt.client as mqtt, ibmiotf.application
from threading import Thread

localizacao = "-23.5062,-47.4559,17km" #coordenada de Sorocaba
#localizacao = "-22.4249222,-46.939116,17km" #coordenada de Mogi Mirim para teste

#------------------------------------------------------------------------------------------------------

hashtagsEmergenciais = ["enchente", "terremoto", "tempestade"]

indiciosTerremoto = ["tremores", "tremor"]
indiciosTempestade = ["chuva forte", "ficando AND escuro", "aumento AND temperatura", "aumentando AND temperatura", "ficando AND quente", "escuro AND derrepente", "quente AND derrepente", "quente AND repente", "nublado", "muitas AND nuvens", "muita AND nuvem"]
hashtagsNormais = indiciosTerremoto + indiciosTempestade
ultimaOcorrencia = {}
qtdeNuvem = {}

mediaTemperatura = 0

#------------------------------------------------------------------------------------------------------

def publicarTweet (api, hashtag, emergencia):
	if emergencia == True:
		tweet = "URGENTE: Possivelmente está ocorrendo " + retornarEvento(hashtag) + ". Tome cuidado! "
		
		if retornarEvento(hashtag) == "tempestade":
			tweet = tweet + "Por causa da tempestade, pode haver enchentes. "
		
		tweet = tweet + str(datetime.datetime.now())
	else:
		tweet = "Há chances de ocorrer " + retornarEvento(hashtag) + ". Tome cuidado! "
		
		if retornarEvento(hashtag) == "tempestade":
			tweet = tweet + "Por causa da tempestade, pode haver enchentes. "
		
		tweet = tweet + str(datetime.datetime.now())

	print ("Tweetado: " + tweet)
	status = api.update_status(status=tweet)

#------------------------------------------------------------------------------------------------------

def retornarEvento (hashtag):
	if hashtag in indiciosTerremoto:
		return "terremoto"
	elif hashtag in indiciosTempestade:
		return "tempestade"
	else:
		return hashtag

#------------------------------------------------------------------------------------------------------

def verificarEmergencia (api, hashtags, ultimaOcorrencia):
	for hashtag in hashtags:
		ultimosTweets = tweepy.Cursor(api.search, q=(hashtag), geocode=localizacao).items(1)
		for tweet in ultimosTweets:
			if ( ( not (hashtag in ultimaOcorrencia) ) or ultimaOcorrencia[hashtag] < datetime.datetime.now()-datetime.timedelta(hours=8) ) and tweet.created_at-datetime.timedelta(hours=3) >= datetime.datetime.now()-datetime.timedelta(hours=8):
				print (hashtag)
				ultimaOcorrencia[hashtag] = tweet.created_at-datetime.timedelta(hours=3)
				print (str(ultimaOcorrencia[hashtag] + datetime.timedelta(hours=8)))
				publicarTweet (api, hashtag, True)

#------------------------------------------------------------------------------------------------------

def verificar (api, hashtags, ultimaOcorrencia, qtdeMin):
	tweetsLidos = {}
	qtde = {}

	for hashtag in hashtags:
		indice = retornarEvento(hashtag)
		qtde[indice] = 0

	for hashtag in hashtags:
		indice = retornarEvento(hashtag)
		ultimosTweets = tweepy.Cursor(api.search, q=(hashtag), geocode=localizacao).items(qtdeMin)

		for tweet in ultimosTweets:
			if ( ( not (hashtag in ultimaOcorrencia) ) or ultimaOcorrencia[hashtag] < datetime.datetime.now()-datetime.timedelta(hours=8) ) and tweet.created_at-datetime.timedelta(hours=3) >= datetime.datetime.now()-datetime.timedelta(hours=8):
				if not tweet.id in tweetsLidos:
					print (hashtag)
					tweetsLidos[tweet.id] = 1
					qtde[indice] += 1
		
		for tweet in ultimosTweets:
			break

		if qtde[indice] >= qtdeMin:
			qtde[indice] = 0
			if ( not (hashtag in ultimaOcorrencia) ) or ultimaOcorrencia[hashtag] < tweet.created_at-datetime.timedelta(hours=3):
				ultimaOcorrencia[hashtag] = tweet.created_at-datetime.timedelta(hours=3)
				print (str(ultimaOcorrencia[hashtag] + datetime.timedelta(hours=8)))
			
			publicarTweet (api, hashtag, False)

#------------------------------------------------------------------------------------------------------

def get_api(cfg):
	auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
	auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
	return tweepy.API(auth)

#------------------------------------------------------------------------------------------------------

def ibmSubCallback(event):
	str = "%s event '%s' received from device [%s]: %s"
	print(str % (event.format, event.event, event.device, json.dumps(event.data)))

	dataIBM = event.data

	verificarDadosNuvem(ultimaOcorrencia, 5, dataIBM)

#------------------------------------------------------------------------------------------------------

def verificarDadosNuvem(ultimaOcorrencia, qtdeMin, dataIBM):
	if 'luminosidade' in dataIBM and dataIBM['luminosidade'] <= 500:
		if 'tempestade' in qtdeNuvem:
			qtdeNuvem['tempestade'] += 1
		else:
			qtdeNuvem['tempestade'] = 1
	
	if 'temp' in dataIBM:
		if not 'mediaTemperatura' in globals():
			global mediaTemperatura
			mediaTemperatura = dataIBM['temp']
		elif mediaTemperatura == 0:
			mediaTemperatura = dataIBM['temp']
		elif dataIBM['temp'] >= 20 and dataIBM['temp']-mediaTemperatura >= 3:
			if 'tempestade' in qtdeNuvem:
				qtdeNuvem['tempestade'] += 1
			else:
				qtdeNuvem['tempestade'] = 1
		else:
			mediaTemperatura = (mediaTemperatura*3+dataIBM['temp'])/4
	
	if 'tilt' in dataIBM and dataIBM['tilt'] == 1:
		if 'terremoto' in qtdeNuvem:
			qtdeNuvem['terremoto'] += 1
		else:
			qtdeNuvem['terremoto'] = 1

	for hashtag in hashtagsEmergenciais:
		if hashtag in qtdeNuvem and qtdeNuvem[hashtag] >= qtdeMin:
			qtdeNuvem[hashtag] = 0
			if ( not (hashtag in ultimaOcorrencia) ) or ultimaOcorrencia[hashtag] < datetime.datetime.now()-datetime.timedelta(hours=8):
				ultimaOcorrencia[hashtag] = datetime.datetime.now()
				publicarTweet (api, hashtag, True)

#------------------------------------------------------------------------------------------------------

cfg = { 
	"consumer_key"        : "GpsI5xzGNeJMyxiytPJy1JKtA",
	"consumer_secret"     : "4ofoirt1ceq9D43BhEJ75NocZmSM31VGjRum64Es4JTIW0gDep",
	"access_token"        : "880398664258244608-wKbULnXQoGI7y0EeFmDwemplqKcrbMe",
	"access_token_secret" : "pVz5wKttqlOxvlLF8YuVsOfN58uOLoQoaoDjvk3hxrF7e" 
	}

api = get_api(cfg)

def main():
	mediaTemperatura = 0
	qtdeNuvem = {}
#--------Conectar na nuvem
	organization = "2yutff"
	deviceType = "DragonBoard"
	deviceId = "1"
	authMethod = "token"
	authToken = "ztyVDSnY&K3be*@eTx"
	authKey = "a-2yutff-wb9yu7vywz"

	try:
		deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken, "auth-key": authKey}
		deviceCli = ibmiotf.application.Client(deviceOptions)
		deviceCli.connect()
	except ibmiotf.ConfigurationException as e:
		print(str(e))
		sys.exit()
	except ibmiotf.UnsupportedAuthenticationMethod as e:
		print(str(e))
		sys.exit()
	except ibmiotf.ConnectionException as e:
		print(str(e))
		sys.exit()
		
	deviceCli.deviceEventCallback = ibmSubCallback
	deviceCli.subscribeToDeviceEvents(deviceType=deviceType)

#--------Inicialização
	
#--------Looping

	while True:
		try:
			print ("Realizando verificacoes do twitter")
			verificarEmergencia(api, hashtagsEmergenciais, ultimaOcorrencia)
			verificar (api, hashtagsNormais, ultimaOcorrencia, 5)
			print ("Verificacoes do twitter realizadas\n")
		except Exception as e:
			print ("\n----------------------------------------------------------------------------------------")
			print ("Erro: " + str(e))
			print ("Sera realizada uma nova tentativa.")
			print ("----------------------------------------------------------------------------------------\n")
			api = get_api(cfg)
			continue
		
		time.sleep(120)


if __name__ == "__main__":
	main()