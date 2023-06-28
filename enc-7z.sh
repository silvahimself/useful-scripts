
7z a -p$Z_ENC_PASSWORD -mhe=on -r -scrc=SHA256 -mx9 -stl '-xr!.var' '-xr!.cache' '-xr!.nuget' '-xr!.local' '-xr!node_modules' '-xr!bin' '-xr!obj' '-xr!snap' ~/bk/data_$(date +%s).7z ~/data/