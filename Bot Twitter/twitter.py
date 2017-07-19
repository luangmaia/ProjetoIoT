import tweepy, datetime, time

#localizacao = "-23.5062,-47.4559,17km" #coordenada de Sorocaba
localizacao = "-22.4249222,-46.939116,17km" #coordenada de Mogi Mirim para teste

#------------------------------------------------------------------------------------------------------

hashtagsEmergenciais = ["enchente", "terremoto", "tempestade"]

indiciosTerremoto = ["tremores", "tremor"]
indiciosTempestade = ["chuva forte", "ficando AND escuro", "aumento AND temperatura", "aumentando AND temperatura", "ficando AND quente", "escuro AND derrepente", "quente AND derrepente", "nublado", "muitas AND nuvens", "muita AND nuvem"]
hashtagsNormais = indiciosTerremoto + indiciosTempestade

#------------------------------------------------------------------------------------------------------

def publicarTweet (api, hashtag, emergencia):
	if emergencia == True:
		tweet = "Possivelmente está ocorrendo " + retornarEvento(hashtag) + " em Sorocaba. Tome cuidado! "
		
		if retornarEvento(hashtag) == "tempestade":
			tweet = tweet + "Por causa da tempestade, pode haver enchentes. "
		
		tweet = tweet + str(datetime.datetime.now())
	else:
		tweet = "Há chances de ocorrer " + retornarEvento(hashtag) + " em Sorocaba. Tome cuidado! "
		
		if retornarEvento(hashtag) == "tempestade":
			tweet = tweet + "Por causa da tempestade, pode haver enchentes. "
		
		tweet = tweet + str(datetime.datetime.now())

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

def retornarEventoSemAcentos (hashtag):
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
				print (ultimaOcorrencia[hashtag] + datetime.timedelta(hours=8))
				publicarTweet (api, hashtag, True)

#------------------------------------------------------------------------------------------------------

def verificar (api, hashtags, ultimaOcorrencia, qtdeMin):
	qtde = {}
	tweetsLidos = {}

	for hashtag in hashtags:
		indice = retornarEventoSemAcentos(hashtag)
		qtde[indice] = 0

	for hashtag in hashtags:
		indice = retornarEventoSemAcentos(hashtag)
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
			if ( not (hashtag in ultimaOcorrencia) ) or ultimaOcorrencia[hashtag] < tweet.created_at-datetime.timedelta(hours=3):
				ultimaOcorrencia[hashtag] = tweet.created_at-datetime.timedelta(hours=3)
				print (ultimaOcorrencia[hashtag] + datetime.timedelta(hours=8))
			
			publicarTweet (api, hashtag, False)

#------------------------------------------------------------------------------------------------------

def get_api(cfg):
	auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
	auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
	return tweepy.API(auth)

#------------------------------------------------------------------------------------------------------

def main():
	# Fill in the values noted in previous step here
	cfg = { 
	"consumer_key"        : "GpsI5xzGNeJMyxiytPJy1JKtA",
	"consumer_secret"     : "4ofoirt1ceq9D43BhEJ75NocZmSM31VGjRum64Es4JTIW0gDep",
	"access_token"        : "880398664258244608-wKbULnXQoGI7y0EeFmDwemplqKcrbMe",
	"access_token_secret" : "pVz5wKttqlOxvlLF8YuVsOfN58uOLoQoaoDjvk3hxrF7e" 
	}

	api = get_api(cfg)
	'''
	ultimosTweets = tweepy.Cursor(api.search, q=("chuva forte 3")).items(10)

	for tweet in ultimosTweets:
		print ((tweet.created_at-datetime.timedelta(hours=3) - datetime.datetime.now()).days)
		print (tweet.created_at-datetime.timedelta(hours=3), tweet.text, tweet.lang)
	'''
	# tweet = "Hello, world!"
	# status = api.update_status(status=tweet) 
	# Yes, tweet is called 'status' rather confusing

#--------Inicialização
	ultimaOcorrencia = {}

#--------Looping

	while True:
		try:
			print ("Realizando verificacoes")
			verificarEmergencia(api, hashtagsEmergenciais, ultimaOcorrencia)
			verificar (api, hashtagsNormais, ultimaOcorrencia, 5)
			print ("Verificacoes realizadas\n")
		except Exception as e:
			print ("\n----------------------------------------------------------------------------------------")
			print ("Erro: " + str(e))
			print ("Sera realizada uma nova tentativa.")
			print ("----------------------------------------------------------------------------------------\n")
			api = get_api(cfg)
			continue
	
		time.sleep(180)


if __name__ == "__main__":
	main()