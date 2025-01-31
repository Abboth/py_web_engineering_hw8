document.getElementById("searchButton").addEventListener("click", async () => {
    const query = document.getElementById("searchInput").value.trim();
    if (!query) {
        alert("Please enter a search term.");
        return;
    }

    try {
        const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }
        const quotes = await response.json();
        displayResults(quotes);
    } catch (error) {
        console.error("Error fetching quotes:", error);
        alert("An error occurred while fetching quotes.");
    }
});

function displayResults(quotes) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = "";

    if (quotes.length === 0) {
        resultsContainer.innerHTML = "<p>No quotes found.</p>";
        return;
    }

    quotes.forEach(quote => {
        const quoteElement = document.createElement("div");
        quoteElement.classList.add("quote");

        const quoteText = document.createElement("p");
        quoteText.textContent = quote.quote;
        quoteElement.appendChild(quoteText);

        const author = document.createElement("div");
        author.classList.add("author");
        author.textContent = `— ${quote.author.fullname}`;
        quoteElement.appendChild(author);

        if (quote.tags && quote.tags.length > 0) {
            const tags = document.createElement("div");
            tags.classList.add("tags");
            tags.textContent = `Tags: ${quote.tags.join(", ")}`;
            quoteElement.appendChild(tags);
        }

        resultsContainer.appendChild(quoteElement);
    });
}