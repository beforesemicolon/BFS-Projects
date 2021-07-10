const users = [];

const uniqueAlphaNumericId = (() => {
  const heyStack = '0123456789abcdefghijklmnopqrstuvwxyz';
  const {length} = heyStack;
  const randomInt = () => Math.floor(Math.random() * length);
  
  return (length = 24) => Array.from({length}, () => heyStack[randomInt()]).join('');
})();

class RegisterService {
  defaultInfo = {
    'first-name': '',
    'last-name': '',
    email: '',
    username: '',
    password: '',
    'password-confirm': ''
  }
  
  validateInfo(info) {
    info = {...this.defaultInfo, ...info};
    
    let errorMessage = '';
    let errorField = '';
  
    for (let key in info) {
      if (info.hasOwnProperty(key) && !info[key]) {
        const field = key.replace('-', ' ');
        return  {
          errorMessage: `The "${field}" field is required.`,
          errorField: key
        };
      }
    }
    
    if (!/[a-zA-Z][a-zA-Z]+/.test(info['first-name'])) {
      errorMessage = 'First name may only contain letters';
      errorField = 'first-name';
    } else if(!/[a-zA-Z][a-zA-Z]+/.test(info['last-name'])) {
      errorMessage = 'Last name may only contain letters';
      errorField = 'last-name';
    } else if(!/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/.test(info.email)) {
      errorMessage = 'Email is of an invalid format';
      errorField = 'email';
    } else if(!/[_a-zA-Z0-9]{6,35}/.test(info.username)) {
      errorMessage = 'Username may only contain letters, numbers, and underscore';
      errorField = 'username';
    } else if(!/(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*#?&]).{8,35}/.test(info.password)) {
      errorMessage = 'Password must be 8-35 characters long containing at least one lower and uppercase letter, number and a symbol';
      errorField = 'password';
    }
    
    if (info.password !== info['password-confirm']) {
      errorMessage = 'Passwords do not match';
      errorField = 'password-confirm';
    }
  
    return {errorMessage, errorField};
  }
  
  saveUser(info) {
    const existingUser = users.find(usr => {
      return usr.email === info.email || usr.username === info.username;
    })
  
    if (existingUser) {
      if (existingUser.username === info.username && existingUser.email !== info.email) {
        return {
          errorMessage: 'This username is already taken',
          errorField: 'username'
        }
      } else {
        return {
          errorMessage: 'User already exists',
          errorField: 'email'
        }
      }
    }
    
    users.push({
      id: uniqueAlphaNumericId(),
      ...info
    })
  }
  
  findUser(email) {
    return users.find(usr => usr.email === email);
  }
}

module.exports.registerService = new RegisterService();
