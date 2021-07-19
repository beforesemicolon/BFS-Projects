const express = require('express');
const http = require('http');
const path = require('path');
const multer = require('multer');
const {engine} = require('@beforesemicolon/html-plus');
const {Field} = require('../src/tags/field');
const {FormPageHeader} = require('../src/tags/formPageHeader');
const {registerService} = require('./register.service');
const session = require('express-session');

const app = express();
const upload = multer();

(async () => {
  app.use(session({
    name: 'session-id',
    // secret: process.env.SESSION_SECRET,
    secret: 'secret',
    saveUninitialized: false,
    resave: false
  }))
  
  app.use((req, res, next) => {
    if (!req.path.startsWith('/register')) {
      if (req.path.startsWith('/login')) {
        if (req.session.user) {
          return res.redirect('/')
        }
      } else if (!req.session.user) {
        return res.redirect('/login')
      }
    }
    
    next();
  })
  
  app.post('/register', upload.none(), (req, res, next) => {
    let result = registerService.validateInfo(req.body);
    
    if (!result.errorMessage) {
      result = registerService.saveUser(req.body);
      
      // if the error is in the email field is because the user
      // already exists and should login
      // it should login is there is no error as well
      if (!result.errorField || result.errorField === 'email') {
        return res.redirect('/login');
      }
    }
    
    res.render('register', {...req.body, ...result});
  });
  
  app.post('/login', upload.none(), (req, res) => {
    const {email, password} = req.body;
    
    if (
      /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/.test(email) &&
      /.{8,35}$/.test(password)
    ) {
      const user = registerService.findUser(email);

      if (user && user.password === password) {
        req.session.user = user;
        return res.redirect('/');
      }
    }
    
    res.render('login', {
      email, password, errorMessage: 'Invalid Email or Password'
    })
  })
  
  await engine(app, path.resolve(__dirname, '../src'), {
    customTags: [Field, FormPageHeader],
    onPageRequest(req) {
      return {user: req.session.user}
    }
  });
  
  const server = http.createServer(app);
  
  server.listen(3000, () => {
    console.log('server live on port 3000')
  })
})()
