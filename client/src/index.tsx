import React from 'react';
import ReactDOM from 'react-dom';
import App from './UI';

const render = (Component: React.ComponentType) => {
  ReactDOM.render(
    <React.StrictMode>
      <Component />
    </React.StrictMode>,
    document.getElementById('root')
  );
};

render(App);

if (module.hot) {
  module.hot.accept('./App', () => {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const NextApp = require('./App').default;
    render(NextApp);
  });
}