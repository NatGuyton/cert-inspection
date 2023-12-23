import react, {useState} from 'react';
import logo from './logo.png';
import './App.css';
import Header from './Components/Header';
import Results from './Components/Results';

function App() {
  const API_URL = 'https://cert-inspection.guyton.net/api';
  const [apiResult, setApiResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  async function fetchApiResult(host) {
    setIsLoading(true);
    setError(null);
    setApiResult(null);
    if (host.length > 0) {
      try {
        const full_url = API_URL + '?pretty&host=' + encodeURIComponent(host);
        const response = await fetch(full_url);
        if (response.status.toString().startsWith('5')) {
          const data = await(response.text());
          throw new Error(`HTTP ${response.status.toString()}: ${data}`);
        }
        if (response.status !== 200) {
          const data = await(response.text());
          throw new Error(`Something went wrong!  HTTP ${response.status.toString()}: ${data}`);
        }
        const data = await response.json();
        setApiResult(data);
      } catch (error) {
        setError(error.message);
      }
    }
    setIsLoading(false);
  }


  return (
    <div className="App">
      {/* Google font, https://developers.google.com/fonts/docs/css2 */}
      <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css2?family=Black+Ops+One" />

      <div className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <Header onInput={fetchApiResult} error={error} />
      </div>
      <div className="App-body">
        <Results data={apiResult} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default App;
