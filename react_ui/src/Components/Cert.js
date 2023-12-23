function Cert(props) {
    let expiredtext = ""
    if (props.data.expired === true) {
        expiredtext = <em style={{color: 'red'}}>EXPIRED</em>;
    }

    let trustedtext = ""
    if (props.data.trusted === true) {
        trustedtext = <> - <em style={{color: 'green'}}>IN TRUST STORE</em></>;
    }

    let sentbyserver = ""
    if (props.data.fromServer === true) {
        sentbyserver = <> - <em style={{color: 'blue'}}>SENT BY SERVER</em></>;
    }

    // colorize validation string appropriately
    let validation = props.data.validation;
    if ((validation === undefined) || (validation === "")) {
        validation = "";
    } else {
        let dashindex = validation.indexOf(" - ", 0);
        if (dashindex !== undefined) {
            if (validation.includes(" - 0:", 0)) {
                validation = <>{validation.slice(0, dashindex)}<em style={{color: 'green'}}>{validation.slice(dashindex)}</em></>;
            } else {
                validation = <>{validation.slice(0, dashindex)}<em style={{color: 'red'}}>{validation.slice(dashindex)}</em></>;
            }
        }
    }

    return (
        <div className="cert">
            <div className="cert-pem">
                <pre>
                    {props.data.cert}
                </pre>
            </div>
            <div className="cert-details">
                Depth: {props.order} {trustedtext} {sentbyserver}
                {validation !== "" && <><br/>Validation: {validation}</>}
                <br/>Subject: {props.data.subject} 
                <br/>Issuer: {props.data.issuer}
                {props.data.hasOwnProperty('subjectAltName') && <><br/>SAN: {props.data.subjectAltName}</>}
                <br/>notBefore: {props.data.notBefore}
                <br/>notAfter: {props.data.notAfter} {expiredtext}
                <br/>Fingerprint: {props.data['SHA-1 fingerprint']}
                {props.data.hasOwnProperty('subjectKeyIdentifier') && <><br/>subjectKeyIdentifier: {props.data.subjectKeyIdentifier}</>}
                {props.data.hasOwnProperty('authorityKeyIdentifier') && <><br/>authorityKeyIdentifier: {props.data.authorityKeyIdentifier}</>}
            </div>
        </div>
    );
}

export default Cert;