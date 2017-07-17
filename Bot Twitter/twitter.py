import tweepy, datetime, time

#localizacao = "-23.5062,-47.4559,17km" #coordenada de Sorocaba
localizacao = "-22.4249222,-46.939116,17km" #coordenada de Mogi Mirim para teste

def publicarTweet (api, hashtag, emergencia):
	if emergencia == True:
		tweet = "Possivelmente está ocorrendo " + retornarEvento(hashtag) + " em Sorocaba. Tome cuidado! " + str(datetime.datetime.now())
	else:
		tweet = "Possivelmente irá ocorrer " + retornarEvento(hashtag) + " em Sorocaba. Tome cuidado! " + str(datetime.datetime.now())
	status = api.update_status(status=tweet)

def retornarEvento (hashtag):
	if hashtag == "furacao":
		return "furacão"
	elif hashtag == "tremores" or hashtag == "tremor":
		return "terremoto"
	elif hashtag == "chuva forte":
		return "tempestade"
	else:
		return hashtag

def verificarEmergencia (api, hashtags, ultimaOcorrencia):
	for hashtag in hashtags:
		ultimosTweets = tweepy.Cursor(api.search, q=(hashtag), geocode=localizacao).items(1)
		for tweet in ultimosTweets:
			if ( ( not (hashtag in ultimaOcorrencia) ) or ( ultimaOcorrencia[hashtag] - datetime.datetime.now() ).days > 0 ) and ( tweet.created_at - datetime.datetime.now() ).days == 0:
				print (hashtag)
				ultimaOcorrencia[hashtag] = tweet.created_at
				publicarTweet (api, hashtag, True)

def verificar (api, hashtags, ultimaOcorrencia):
	for hashtag in hashtags:
		qtde = 0
		ultimosTweets = tweepy.Cursor(api.search, q=(hashtag), geocode=localizacao).items(5)

		for tweet in ultimosTweets:
			if ( ( not (hashtag in ultimaOcorrencia) ) or ( ultimaOcorrencia[hashtag] - datetime.datetime.now() ).days > 0 ) and ( tweet.created_at - datetime.datetime.now() ).days == 0:
				print (hashtag)
				qtde += 1
		
		if qtde >= 5:
			if ( not (hashtag in ultimaOcorrencia) ) or ultimaOcorrencia[hashtag] < tweet.created_at:
					ultimaOcorrencia[hashtag] = tweet.created_at
			
			publicarTweet (api, hashtag, False)

def get_api(cfg):
	auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
	auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
	return tweepy.API(auth)

def main():
	# Fill in the values noted in previous step here
	cfg = { 
	"consumer_key"        : "GpsI5xzGNeJMyxiytPJy1JKtA",
	"consumer_secret"     : "4ofoirt1ceq9D43BhEJ75NocZmSM31VGjRum64Es4JTIW0gDep",
	"access_token"        : "880398664258244608-wKbULnXQoGI7y0EeFmDwemplqKcrbMe",
	"access_token_secret" : "pVz5wKttqlOxvlLF8YuVsOfN58uOLoQoaoDjvk3hxrF7e" 
	}

	api = get_api(cfg)

	# tweet = "Hello, world!"
	# status = api.update_status(status=tweet) 
	# Yes, tweet is called 'status' rather confusing

#--------Inicialização
	hashtagsEmergenciais = ["enchente", "furacao", "terremoto", "tempestade"]
	hashtagsNormais = ["tremor", "tremores", "chuva forte"]
	ultimaOcorrencia = {}

#--------Looping
	while True:
		try:
			verificarEmergencia(api, hashtagsEmergenciais, ultimaOcorrencia)
			verificar (api, hashtagsNormais, ultimaOcorrencia)
		except Exception as e:
			api = get_api(cfg)
			continue
		
		time.sleep(120)

#	ultimosTweets = tweepy.Cursor(api.search, q=("sorocaba"), geocode=localizacao).items(10)

#	for tweet in ultimosTweets:
#		print ((tweet.created_at - datetime.datetime.now()).days)
#		print (tweet.created_at, tweet.text, tweet.lang)

if __name__ == "__main__":
	main()