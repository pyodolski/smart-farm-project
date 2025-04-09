//1. app.py 실행 

  http://127.0.0.1:5000 사용X

//2. new Terminal 
    farm1>에서 cd front 후 npm start

    
--------------------------------------------
                            오류 대처 
            
npm error code ENOENT
npm error syscall open
npm error path C:\Users\\package.json
....

**위 오류 발생시** npm install 




**react-router-dom 오류 발생시** 
npm install react-router-dom --save




Access to XMLHttpRequest at 'http://localhost:5000/' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.

**위 오류 발생시** pip install flask_cors
