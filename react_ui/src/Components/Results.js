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
                    <p>
                        Some good candidates at <a href="https://badssl.com/">https://badssl.com/</a>.
                    </p>
                </div>
            </>
        );
    }

    const results = props.data.results;
    // console.log(results);
    return (
        <div className="results">
            <p>
                Hostname: {results.connection.hostname}  Port: {results.connection.port}
                <br/>SNI Servername: {results.connection.servername}
                {results.connection.servername !== results.connection.hostname && <><br />Servername: {results.connection.servername}</>}
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