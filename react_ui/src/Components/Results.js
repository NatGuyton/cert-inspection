import Cert from './Cert';

function Results(props) {
    // if props.data does not exist, return instruction page
    if (props.data === null) {
        return (
            <>
                <div className="error">
                    {props.error}
                </div>
                <div className="results">
                    <h2>Instructions</h2>
                    <p>Enter one of the following and hit enter:</p>
                    <ul>
                        <li>hostname</li>
                        <li>hostname:port</li>
                        <li>URL</li>
                    </ul>
                    <p>Advanced Mode</p>
                    <ul>
                        <li>Target should contain hostname[:port], IP address[:port], or URL for the endpoint you want to reach</li>
                        <li>Servername should contain the SNI name on the cert you wish to inspect, assuming it is not the default.   You can also specify a nonsense value such as "default" to get the default cert.</li>
                    </ul>
                </div>
            </>
        );
    }

    const results = props.data.results;

    return (
        <div className="results">
            <p>
                Hostname: {results.connection.hostname}  Port: {results.connection.port}
                {results.connection.servername !== results.connection.hostname && <><br />SNI Servername: {results.connection.servername}</>}
                <br />Connection: {results.connection.protocol} {results.connection.bits} bits using {results.connection.cipher}
            </p>
            {/* Loop through results.certs and present each cert object */}
            {Object.keys(results.certs).map((key, index) => (
                <Cert key={key} order={key} data={results.certs[key]} />
            ))}
        </div>
    )
}

export default Results;