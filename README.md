# dc_matrix_pond


```
pip install redis
```

# Pond
```
docker-compose up
python aquarium.py
```

# Vivisystem
```
python server.py
ngrok tcp 8016 
```

# Redis
UI accessible at http://localhost:7843 
exec into sentinel
```
docker exec -it dc_matrix_pond_redis-sentinel_1 redis-cli -p 26379
SENTINEL get-master-addr-by-name redismaster
```

# Test different ponds
```
python aquarium.py
python aquarium.py some-other-pond
```

