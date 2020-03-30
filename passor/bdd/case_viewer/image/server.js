const express = require('express')
const app = express()
const port = 80

app.get('/update', (request, response) => {
  var exec = require('child_process').execSync;
  var cmdStr = './html_gen.sh';
  //var resp = 'Request accepted!';
  var resp = exec(cmdStr, function(err,stdout,stderr){
      if(err) {
          console.log('git pull failed:'+stderr);
          resp='Found error!'
      } else {
          //var data = JSON.parse(stdout);
          //console.log(data);
          console.log(stdout)
        }
    });
  response.send('<html><body><pre>'+resp+'</pre></body>')
});


app.use(express.static('/html'))
app.listen(port, (err) => {
  if (err) {
    return console.log('internal server error', err)
  }

  console.log(`server is listening on ${port}`)
})