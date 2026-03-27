- For our backend code I used MyPy, Bandit, and PyLint
- I installed it to the local environment with the following command:
```
 ~/Projects/CSE-3311/CSE-3311-$ .venv/bin/python3 -m pip install mypy
 ~/Projects/CSE-3311/CSE-3311-$ .venv/bin/python3 -m pip install bandit
 ~/Projects/CSE-3311/CSE-3311-$ .venv/bin/python3 -m pip install pylint
```
- For the frontend I used Flow which I installed with the below command
```
 ~/Projects/CSE-3311/CSE-3311-$ npm install --save-dev @babel/core @babel/cli @babel/preset-flow babel-plugin-syntax-hermes-parser
npm install --save-dev flow-bin
```
- Then I  created a `.babelrc` file and added library type definitions
```
npm install -g flow-typed
Flow-typed install
```
Additionally the header `// @jsx h` needed to be added to all of our `.jsx` files to be detected by Flow.

I also added ESLint for the front end, I installed it with
`npm init @eslint/config@latest`

I added all of the static analysis tools to our makefile
