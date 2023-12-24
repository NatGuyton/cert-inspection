import {useState} from 'react';
import Form from 'react-bootstrap/Form';
import Button  from 'react-bootstrap/Button';
import { useHashFragment } from '../Hooks/HashFragment';

function Header(props) {
    const [advancedChecked, setAdvancedChecked] = useState(false);

    // detect hash change, set input bar, fetch query
    useHashFragment(props.onInput);

    function clearTarget() {
        window.location.href = window.location.href.split('#')[0] + `#/`;
    }

    function handleFindTarget() {
        // If pressing button for a repeat fetch, button should trigger query, otherwise url change will handle it
        const {hash} = window.location;
        let actual_hash = hash.slice(2);
        if (actual_hash === document.getElementById('host').value) {
            props.onInput(actual_hash);
        } else {
            if (document.getElementById('servername').value.trim() === "") {
                window.location.href = window.location.href.split('#')[0] + `#/${document.getElementById('host').value.trim()}`;
            } else {
                window.location.href = window.location.href.split('#')[0] + `#/${document.getElementById('host').value.trim()}/#/${document.getElementById('servername').value.trim()}`;
            }
        }
    }

    // https://codingbeautydev.com/blog/react-get-input-value-on-enter/
    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            if (document.getElementById('servername').value.trim() === "") {
                window.location.href = window.location.href.split('#')[0].replace(/\?$/, '') + `#/${document.getElementById('host').value.trim()}`;
            } else {
                window.location.href = window.location.href.split('#')[0].replace(/\?$/, '') + `#/${document.getElementById('host').value.trim()}/#/${document.getElementById('servername').value.trim()}`;
            }
        }
    }

    function toggleAdvancedMode() {
        if (advancedChecked) {
            setAdvancedChecked(false);
        } else {
            setAdvancedChecked(true);
        }
    }
    let advButtonVariant = "outline-secondary";
    let inputForm = <Form.Group className="mb-3">
        <Form.Label>Target</Form.Label>
        <Form.Control id="host" aria-describedby="basic-addon3" onKeyDown={handleKeyDown} />
        <input type="hidden" id="servername" value=""></input>
    </Form.Group>
    if (advancedChecked) {
        advButtonVariant = "primary";
        inputForm = <><Form.Group className="advForm">
            <Form.Label className="dropSlightly">Target</Form.Label>
            &nbsp; <Form.Control id="host" aria-describedby="basic-addon3" onKeyDown={handleKeyDown} />
        </Form.Group>
        <Form.Group className="advForm mb-3">
            <Form.Label className="dropSlightly">ServerName</Form.Label>
            &nbsp; <Form.Control id="servername" aria-describedby="basic-addon3" onKeyDown={handleKeyDown} />
        </Form.Group></>
    }

    return (
        <header className='App-header-input'>
            <div>
                <div className="titleBar">
                    <div className="title">Cert Inspection</div>
                    <Button variant={advButtonVariant} onClick={toggleAdvancedMode}>Advanced</Button>
                </div>
                <div>
                    <Form>
                        {inputForm}
                    </Form>
                </div>
                <p className="error">
                    {props.error}
                </p>
            </div>
        </header>
    )
}

export default Header;
