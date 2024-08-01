import React from 'react';
import ReactDOM from 'react-dom';
import UI from './UI';

const render = (Component: React.ComponentType) => {
  ReactDOM.render(
    <React.StrictMode>
      <Component />
    </React.StrictMode>,
    document.getElementById('root')
  );
};

render(UI);

if (import.meta.hot) {
  import.meta.hot.accept();
  const NextApp = require('./UI').default;
  render(NextApp);
}
