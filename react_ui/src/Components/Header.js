import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import InputGroup from 'react-bootstrap/InputGroup';
import { useHashFragment } from '../Hooks/HashFragment';

function Header(props) {
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
            window.location.href = window.location.href.split('#')[0] + `#/${document.getElementById('host').value.trim()}`;
        }
    }
    // https://codingbeautydev.com/blog/react-get-input-value-on-enter/
    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            window.location.href = window.location.href.split('#')[0] + `#/${document.getElementById('host').value.trim()}`;
        }
    }

    return (
        <header className='App-header-input'>
            <div>
                <div className="title">Cert Inspection</div>
                <div>
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Target</Form.Label>
                            <Form.Control id="host" aria-describedby="basic-addon3" onKeyDown={handleKeyDown} />
                        </Form.Group>
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
