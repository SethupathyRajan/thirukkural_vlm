import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <nav className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0">
              <Link to="/" className="text-xl font-semibold text-gray-800">
                Thirukkural Educational AI
              </Link>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link to="/" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  Home
                </Link>
                <Link to="/results" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  Results
                </Link>
                <Link to="/chat" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  Chat
                </Link>
                <Link to="/about" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  About
                </Link>
                <Link to="/research" className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium">
                  Research
                </Link>
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="ml-4 flex items-baseline space-x-4">
              {/* Placeholder for user actions (e.g., login, theme) */}
              <button className="text-gray-500 hover:text-gray-700">
                User
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar