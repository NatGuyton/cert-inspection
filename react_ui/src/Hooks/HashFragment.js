import { useEffect } from "react";

export function useHashFragment(onInput, trigger=true) {
    useEffect(() => {

        function hashChanged() {
            const {hash} = window.location;
            let actual_hash = hash.slice(2);
            document.getElementById('host').value = actual_hash;
            onInput(actual_hash);
        }

        if (!trigger) return;

        hashChanged();

        window.addEventListener('hashchange', hashChanged);
        return () => window.removeEventListener('hashchange', hashChanged);

    }, [trigger]);
}