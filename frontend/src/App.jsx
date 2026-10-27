
import { useState } from 'react'
import './App.css'

function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const [issues, setIssues] = useState([])
  const [savedIssues, setSavedIssues] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('issuelens-saved-issues')) || []
    } catch {
      return []
    }
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [hasSearched, setHasSearched] = useState(false)
  const [repositoryDetails, setRepositoryDetails] = useState(null)
  const [showSavedOnly, setShowSavedOnly] = useState(false)

  async function handleSearch(event) {
    event.preventDefault()

    const query = searchQuery.trim()

    if (!query) {
      setError('Enter a repository or topic to search.')
      return
    }

    setLoading(true)
    setError('')
    setHasSearched(true)
    setIssues([])
    setRepositoryDetails(null)

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/search/?q=${encodeURIComponent(query)}&limit=10`
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Unable to search GitHub issues.')
      }

      setIssues(data.items || [])

      const firstIssue = (data.items || [])[0]

      if (firstIssue?.repository) {
        const [owner, repo] = firstIssue.repository.split('/')

        const repoResponse = await fetch(
          `http://127.0.0.1:8000/api/repository/?owner=${encodeURIComponent(owner)}&repo=${encodeURIComponent(repo)}`
        )

        const repoData = await repoResponse.json()

        if (repoResponse.ok) {
          setRepositoryDetails(repoData)
        }
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveIssue = (issue) => {
    const alreadySaved = savedIssues.some(
      (savedIssue) => savedIssue.url === issue.url
    )

    const updatedSavedIssues = alreadySaved
      ? savedIssues.filter((savedIssue) => savedIssue.url !== issue.url)
      : [...savedIssues, issue]

    setSavedIssues(updatedSavedIssues)
    localStorage.setItem(
      'issuelens-saved-issues',
      JSON.stringify(updatedSavedIssues)
    )
  }

  return (
    <div className="app">
      <header className="navbar">
        <h1 className="logo">IssueLens</h1>
        <span className="tagline">Your open-source journey starts here</span>
      </header>

      <main className="main-content">
        <section className="hero">
          <p className="eyebrow">FIND YOUR FIRST CONTRIBUTION</p>
          <h2>Find issues worth solving.</h2>
          <p className="description">
            Discover GitHub issues, explore repositories, and understand
            where your skills can make a difference.
          </p>

          <form className="search-form" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="Try repo:psf/requests"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Searching...' : 'Search issues'}
            </button>
          </form>
        </section>

        <section className="results-section">
          
          <div className="view-switcher">
            <button type="button" onClick={() => setShowSavedOnly(false)}>
              Search issues
            </button>

            <button type="button" onClick={() => setShowSavedOnly(true)}>
              Saved issues ({savedIssues.length})
            </button>
          </div>

          <h3>{hasSearched ? 'Search results' : 'Start exploring'}</h3>

          {repositoryDetails && (
            <div className="repository-summary">
              <h4>{repositoryDetails.name}</h4>
              <p>{repositoryDetails.description}</p>
              <p>
                ⭐ {repositoryDetails.stars.toLocaleString()} stars
                {' · '}
                {repositoryDetails.language || 'Unknown language'}
                {' · '}
                {repositoryDetails.open_issues.toLocaleString()} open issues
              </p>
              <a href={repositoryDetails.url} target="_blank" rel="noreferrer">
                View repository on GitHub →
              </a>
            </div>
          )}


          {loading && <p>Searching GitHub for open issues...</p>}

          {error && <p role="alert">{error}</p>}

          {!loading && !error && hasSearched && issues.length === 0 && (
            <p>No issues found. Try another repository or topic.</p>
          )}

          {!loading && !error && !hasSearched && (
            <p>
              Search for a repository or topic to discover open-source issues.
            </p>
          )}

          {!loading && issues.length > 0 && (
            <div className="issue-list">
              {(showSavedOnly ? savedIssues : issues).map((issue) => (
                <article className="issue-card" key={issue.url}>
                  <h4>
                    <a href={issue.url} target="_blank" rel="noreferrer">
                      {issue.title}
                    </a>
                  </h4>

                  <p className="issue-repository">{issue.repository}</p>

                  <div className="issue-labels">
                    {issue.labels.map((label) => (
                      <span className="issue-label" key={label}>
                        {label}
                      </span>
                    ))}
                  </div>
                  
                  <button
                    type="button"
                    onClick={() => handleSaveIssue(issue)}
                  >
                    {savedIssues.some((savedIssue) => savedIssue.url === issue.url)
                      ? 'Remove saved issue'
                      : 'Save issue'}
                  </button>

                  <a
                    className="issue-link"
                    href={issue.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View issue on GitHub →
                  </a>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
