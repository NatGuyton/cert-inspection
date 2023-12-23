function Cert(props) {
    let expiredtext = ""
    if (props.data.expired === true) {
        expiredtext = <em className="red">EXPIRED</em>;
    }

    let trustedtext = ""
    if (props.data.trusted === true) {
        trustedtext = <> - <em className="green">IN TRUST STORE</em></>;
    }

    let sentbyserver = ""
    if (props.data.fromServer === true) {
        sentbyserver = <> - <em className="blue">SENT BY SERVER</em></>;
    }

    // colorize validation string appropriately
    let validation = props.data.validation;
    if ((validation === undefined) || (validation === "")) {
        validation = "";
    } else {
        let dashindex = validation.indexOf(" - ", 0);
        if (dashindex !== undefined) {
            if (validation.includes(" - 0:", 0)) {
                validation = <>{validation.slice(0, dashindex)}<em className="green">{validation.slice(dashindex)}</em></>;
            } else {
                validation = <>{validation.slice(0, dashindex)}<em className="red">{validation.slice(dashindex)}</em></>;
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
                Depth: <span className="value">{props.order}</span> {trustedtext} {sentbyserver}
                {validation !== "" && <><br/>Validation: <span className="value">{validation}</span></>}
                <br/>Subject: <span className="value">{props.data.subject}</span>
                <br/>Issuer: <span className="value">{props.data.issuer}</span>
                {props.data.hasOwnProperty('subjectAltName') && <><br/>SAN: <span className="value">{props.data.subjectAltName}</span></>}
                <br/>notBefore: <span className="value">{props.data.notBefore}</span>
                <br/>notAfter: <span className="value">{props.data.notAfter} {expiredtext}</span>
                {props.data.hasOwnProperty('keyUsage') && <><br/>keyUsage: <span className="value">{props.data.keyUsage}</span></>}
                {props.data.hasOwnProperty('extendedKeyUsage') && <><br/>extendedKeyUsage: <span className="value">{props.data.extendedKeyUsage}</span></>}
                {props.data.hasOwnProperty('basicConstraints') && <><br/>basicConstraints: <span className="value">{props.data.basicConstraints}</span></>}
                {props.data.hasOwnProperty('signature_algorithm') && <><br/>signatureAlgorithm: <span className="value">{props.data.signature_algorithm}</span></>}
                {props.data.hasOwnProperty('serialnumber') && <><br/>serialNumber: <span className="value">{props.data.serialnumber}</span></>}
                <br/>Fingerprint: <span className="value">{props.data['SHA-1 fingerprint']}</span>
                {props.data.hasOwnProperty('subjectKeyIdentifier') && <><br/>subjectKeyIdentifier: <span className="value">{props.data.subjectKeyIdentifier}</span></>}
                {props.data.hasOwnProperty('authorityKeyIdentifier') && <><br/>authorityKeyIdentifier: <span className="value">{props.data.authorityKeyIdentifier}</span></>}
            </div>
        </div>
    );
}

export default Cert;
