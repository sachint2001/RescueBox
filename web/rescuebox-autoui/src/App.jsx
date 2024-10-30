import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState(null);

    useEffect(() => {
        // Retrieve JSON data from the script tag
        const dataScript = document.getElementById("tree");
        console.log(dataScript);
        const jsonData = JSON.parse(dataScript.textContent);
        console.log(jsonData);
        setData(jsonData);
    }, []);

    if (!data) return <p>Loading...</p>;

    return (
        <div>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    );
}

export default App
