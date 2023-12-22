function Cert(props) {
    let expiredtext = ""
    if (props.data.expired === true) {
        expiredtext = <em style={{color: 'red'}}>EXPIRED</em>;
    }

    let trustedtext = ""
    if (props.data.trusted === true) {
        trustedtext = <em style={{color: 'green'}}>IN TRUST STORE</em>;
    }
    return (
        <div className="cert">
            <br/>Depth: {props.order}
            {props.data.validation !== "" && <><br/>Validation: {props.data.validation}</>}
            <br/>Subject: {props.data.subject} {trustedtext}
            <br/>Issuer: {props.data.issuer}
            {props.data.hasOwnProperty('subjectAltName') && <><br/>SAN: {props.data.subjectAltName}</>}
            <br/>notBefore: {props.data.notBefore}
            <br/>notAfter: {props.data.notAfter} {expiredtext}
            <br/>Fingerprint: {props.data['SHA-1 fingerprint']}
            {props.data.hasOwnProperty('subjectKeyIdentifier') && <><br/>subjectKeyIdentifier: {props.data.subjectKeyIdentifier}</>}
            {props.data.hasOwnProperty('authorityKeyIdentifier') && <><br/>authorityKeyIdentifier: {props.data.authorityKeyIdentifier}</>}
        </div>
    );
}

export default Cert;