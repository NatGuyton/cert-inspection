import { useEffect } from "react";

export function useHashFragment(onInput, trigger=true) {
    useEffect(() => {

        function hashChanged() {
            const {hash} = window.location;
            let actual_hash = hash.slice(2);
            // if actual_hash contains "/#/", set host element to the first part and servername element to the second part
            if (actual_hash.includes("/#/")) {
                document.getElementById('host').value = actual_hash.split("/#/")[0];
                document.getElementById('servername').value = actual_hash.split("/#/")[1];
            } else {
                document.getElementById('host').value = actual_hash;
                document.getElementById('servername').value = "";    
            }
            onInput(actual_hash);
        }

        if (!trigger) return;

        hashChanged();

        window.addEventListener('hashchange', hashChanged);
        return () => window.removeEventListener('hashchange', hashChanged);

    }, [trigger]);
}