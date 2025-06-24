import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [currentView, setCurrentView] = useState('casino');
  const [offers, setOffers] = useState([]);
  const [calls, setCalls] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loginPassword, setLoginPassword] = useState('');
  const [showLogin, setShowLogin] = useState(false);
  const [analytics, setAnalytics] = useState(null);

  // Formulaire pour offres
  const [offerForm, setOfferForm] = useState({
    title: '',
    bonus: '',
    description: '',
    color: '',
    logo: '',
    link: '',
    tags: ''
  });

  // Formulaire pour calls
  const [callForm, setCallForm] = useState({
    slot: '',
    username: ''
  });

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadOffers();
    loadCalls();
    checkAdminStatus();
    setupEventSource();
  }, []);

  const loadOffers = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/offers`);
      const data = await response.json();
      setOffers(data);
    } catch (error) {
      console.error('Erreur lors du chargement des offres:', error);
    }
  };

  const loadCalls = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/calls`);
      const data = await response.json();
      setCalls(data.calls);
    } catch (error) {
      console.error('Erreur lors du chargement des calls:', error);
    }
  };

  const checkAdminStatus = () => {
    const adminCookie = document.cookie.split(';').find(c => c.trim().startsWith('admin='));
    setIsAdmin(adminCookie && adminCookie.split('=')[1] === 'true');
  };

  const setupEventSource = () => {
    const eventSource = new EventSource(`${BACKEND_URL}/api/calls`);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setCalls(data.calls);
    };
    return () => eventSource.close();
  };

  const handleLogin = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ password: loginPassword })
      });

      if (response.ok) {
        setIsAdmin(true);
        setShowLogin(false);
        setLoginPassword('');
        loadAnalytics();
      } else {
        alert('Mot de passe incorrect');
      }
    } catch (error) {
      console.error('Erreur de connexion:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/logout`, {
        method: 'POST',
        credentials: 'include'
      });
      setIsAdmin(false);
      setAnalytics(null);
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
    }
  };

  const loadAnalytics = async () => {
    if (!isAdmin) return;
    try {
      const response = await fetch(`${BACKEND_URL}/api/analytics`, {
        credentials: 'include'
      });
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Erreur lors du chargement des analytics:', error);
    }
  };

  const handleOfferSubmit = async (e) => {
    e.preventDefault();
    try {
      const tagsArray = offerForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag);
      const offerData = { ...offerForm, tags: tagsArray };

      const response = await fetch(`${BACKEND_URL}/api/offers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(offerData)
      });

      if (response.ok) {
        setOfferForm({ title: '', bonus: '', description: '', color: '', logo: '', link: '', tags: '' });
        loadOffers();
        alert('Offre ajoutée avec succès!');
      }
    } catch (error) {
      console.error('Erreur lors de l\'ajout de l\'offre:', error);
    }
  };

  const handleCallSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${BACKEND_URL}/api/calls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(callForm)
      });

      if (response.ok) {
        setCallForm({ slot: '', username: '' });
        loadCalls();
        alert('Call ajouté avec succès!');
      }
    } catch (error) {
      console.error('Erreur lors de l\'ajout du call:', error);
    }
  };

  const handleOfferClick = async (offerId) => {
    try {
      await fetch(`${BACKEND_URL}/api/click`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ offer_id: offerId, user_ip: 'web' })
      });
    } catch (error) {
      console.error('Erreur lors du tracking du clic:', error);
    }
  };

  const deleteCall = async (index) => {
    if (!isAdmin) return;
    try {
      await fetch(`${BACKEND_URL}/api/calls/${index}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      loadCalls();
    } catch (error) {
      console.error('Erreur lors de la suppression du call:', error);
    }
  };

  const resetCalls = async () => {
    if (!isAdmin) return;
    if (window.confirm('Êtes-vous sûr de vouloir vider toute la liste?')) {
      try {
        await fetch(`${BACKEND_URL}/api/calls/reset`, {
          method: 'POST',
          credentials: 'include'
        });
        loadCalls();
      } catch (error) {
        console.error('Erreur lors du reset des calls:', error);
      }
    }
  };

  const deleteOffer = async (offerId) => {
    if (!isAdmin) return;
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette offre?')) {
      try {
        await fetch(`${BACKEND_URL}/api/offers/${offerId}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        loadOffers();
        loadAnalytics();
      } catch (error) {
        console.error('Erreur lors de la suppression de l\'offre:', error);
      }
    }
  };

  const Navigation = () => (
    <nav className="fixed top-0 w-full z-50 bg-gradient-to-r from-yellow-400 via-orange-500 to-red-600 shadow-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center space-x-3">
            <span className="text-2xl font-extrabold tracking-wide text-white drop-shadow-sm">
              🎰 SKRYMI
            </span>
          </div>
          <div className="flex space-x-4 items-center">
            <button
              onClick={() => setCurrentView('casino')}
              className={`px-4 py-2 rounded-full font-semibold transition ${
                currentView === 'casino' ? 'bg-white text-red-600' : 'text-white hover:bg-white/20'
              }`}
            >
              🎲 Casino
            </button>
            <button
              onClick={() => setCurrentView('calls')}
              className={`px-4 py-2 rounded-full font-semibold transition ${
                currentView === 'calls' ? 'bg-white text-red-600' : 'text-white hover:bg-white/20'
              }`}
            >
              📞 Calls
            </button>
            {isAdmin && (
              <button
                onClick={() => setCurrentView('admin')}
                className={`px-4 py-2 rounded-full font-semibold transition ${
                  currentView === 'admin' ? 'bg-white text-red-600' : 'text-white hover:bg-white/20'
                }`}
              >
                ⚙️ Admin
              </button>
            )}
            {isAdmin ? (
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-full text-white font-semibold transition"
              >
                Déconnexion
              </button>
            ) : (
              <button
                onClick={() => setShowLogin(true)}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-full text-white font-semibold transition"
              >
                Admin
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );

  const CasinoView = () => (
    <div className="pt-24 px-4 min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-orange-500 to-red-600 mb-4">
            🎰 Offres Casino Exclusives
          </h1>
          <p className="text-xl text-gray-300">Découvrez les meilleures offres de nos partenaires casino</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {offers.map((offer, index) => (
            <div
              key={offer.id}
              className="rounded-xl shadow-2xl p-6 transform hover:scale-105 transition-all duration-300 cursor-pointer"
              style={{ background: offer.color }}
              onClick={() => {
                handleOfferClick(offer.id);
                window.open(offer.link, '_blank');
              }}
            >
              <div className="flex items-center gap-3 mb-4">
                <img src={offer.logo} alt={offer.title} className="w-12 h-12 rounded-lg shadow-lg" />
                <span className="font-bold text-white text-lg bg-white/20 px-3 py-1 rounded-full">
                  {offer.title.toUpperCase()}
                </span>
              </div>
              <h2 className="text-2xl font-extrabold text-white mb-3">{offer.bonus}</h2>
              <p className="text-white/90 mb-4 text-sm leading-relaxed">{offer.description}</p>
              {offer.tags && offer.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {offer.tags.map((tag, i) => (
                    <span key={i} className="bg-black/40 text-white text-xs px-2 py-1 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              <div className="flex justify-between items-center">
                <button className="bg-white text-black font-bold py-2 px-6 rounded-lg hover:bg-gray-100 transition-colors">
                  Obtenir l'offre
                </button>
                {isAdmin && (
                  <div className="flex gap-2">
                    <span className="text-white/70 text-sm">👆 {offer.clicks || 0}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteOffer(offer.id);
                      }}
                      className="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs"
                    >
                      ✕
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const CallsView = () => (
    <div className="pt-24 px-4 min-h-screen bg-gradient-to-b from-red-950 via-red-900 to-red-800">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-blue-500 to-indigo-400 mb-2">
            Liste des Calls - Skrymi
          </h1>
          <div className="text-xs text-gray-400 mb-6 space-x-2">
            <a href="https://dlive.tv/skrymi" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 transition">📺 DLive</a>
            <span>•</span>
            <a href="https://kick.com/skrymi" target="_blank" rel="noopener noreferrer" className="hover:text-green-400 transition">🎯 Kick</a>
            <span>•</span>
            <a href="https://www.twitch.tv/skrymi" target="_blank" rel="noopener noreferrer" className="hover:text-purple-400 transition">🎮 Twitch</a>
            <span>•</span>
            <a href="https://www.youtube.com/@skrymi777" target="_blank" rel="noopener noreferrer" className="hover:text-red-400 transition">▶ YouTube</a>
          </div>
          <p className="text-gray-400">🗓 {calls.length} call{calls.length !== 1 ? 's' : ''} en attente</p>
        </div>

        <div className="mb-8 bg-black/20 p-6 rounded-lg shadow-inner">
          <h2 className="text-xl font-bold mb-4 text-white">📩 Propose ta slot !</h2>
          <form onSubmit={handleCallSubmit} className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Nom de la slot"
                value={callForm.slot}
                onChange={(e) => setCallForm({...callForm, slot: e.target.value})}
                className="w-full pl-10 pr-4 py-3 rounded-lg bg-gray-800 text-white border border-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <span className="absolute left-3 top-3 text-lg">🎰</span>
            </div>
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Ton pseudo"
                value={callForm.username}
                onChange={(e) => setCallForm({...callForm, username: e.target.value})}
                className="w-full pl-10 pr-4 py-3 rounded-lg bg-gray-800 text-white border border-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <span className="absolute left-3 top-3 text-lg">👤</span>
            </div>
            <button
              type="submit"
              className="bg-green-500 hover:bg-green-600 px-6 py-3 rounded-lg font-semibold text-white transition-colors"
            >
              Envoyer
            </button>
          </form>
        </div>

        {isAdmin && (
          <div className="mb-6 flex gap-4">
            <button
              onClick={resetCalls}
              className="bg-yellow-500 hover:bg-yellow-600 px-4 py-2 rounded-lg text-black font-semibold transition"
            >
              🧽 Vider la liste
            </button>
          </div>
        )}

        <div className="space-y-4">
          {calls.map((call, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-500 p-6 rounded-2xl shadow-lg flex justify-between items-center transform hover:scale-105 transition-all duration-300"
            >
              <div className="text-left">
                <p className="text-xl font-semibold text-white">🎰 {call.slot}</p>
                <p className="text-sm text-gray-100">👤 {call.user}</p>
              </div>
              {isAdmin && (
                <button
                  onClick={() => deleteCall(index)}
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg text-white font-bold transition"
                >
                  Supprimer
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const AdminView = () => (
    <div className="pt-24 px-4 min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">⚙️ Panneau d'Administration</h1>
        
        {analytics && (
          <div className="mb-8 bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-bold text-white mb-4">📊 Analytics</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-600 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-white">{analytics.total_clicks}</div>
                <div className="text-blue-200">Clics totaux</div>
              </div>
              <div className="bg-green-600 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-white">{analytics.total_calls}</div>
                <div className="text-green-200">Calls totaux</div>
              </div>
              <div className="bg-purple-600 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-white">{offers.length}</div>
                <div className="text-purple-200">Offres actives</div>
              </div>
            </div>
            <div className="bg-gray-700 p-4 rounded-lg">
              <h3 className="font-bold text-white mb-2">Clics par offre:</h3>
              <div className="space-y-2">
                {analytics.offers_stats.map((stat, index) => (
                  <div key={index} className="flex justify-between text-gray-300">
                    <span>{stat.title}</span>
                    <span className="font-bold">{stat.clicks} clics</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="bg-gray-800 p-6 rounded-lg mb-8">
          <h2 className="text-xl font-bold text-white mb-4">➕ Ajouter une offre casino</h2>
          <form onSubmit={handleOfferSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Titre"
              value={offerForm.title}
              onChange={(e) => setOfferForm({...offerForm, title: e.target.value})}
              className="p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              type="text"
              placeholder="Bonus"
              value={offerForm.bonus}
              onChange={(e) => setOfferForm({...offerForm, bonus: e.target.value})}
              className="p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              type="text"
              placeholder="Description"
              value={offerForm.description}
              onChange={(e) => setOfferForm({...offerForm, description: e.target.value})}
              className="p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              type="text"
              placeholder="Couleur (ex: linear-gradient(to right, #ff0000, #00ff00))"
              value={offerForm.color}
              onChange={(e) => setOfferForm({...offerForm, color: e.target.value})}
              className="p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              type="url"
              placeholder="URL du logo"
              value={offerForm.logo}
              onChange={(e) => setOfferForm({...offerForm, logo: e.target.value})}
              className="p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              type="url"
              placeholder="Lien d'affiliation"
              value={offerForm.link}
              onChange={(e) => setOfferForm({...offerForm, link: e.target.value})}
              className="p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              type="text"
              placeholder="Tags (séparés par des virgules)"
              value={offerForm.tags}
              onChange={(e) => setOfferForm({...offerForm, tags: e.target.value})}
              className="p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 md:col-span-2"
            />
            <button
              type="submit"
              className="md:col-span-2 bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-semibold text-white transition-colors"
            >
              Ajouter l'offre
            </button>
          </form>
        </div>
      </div>
    </div>
  );

  const LoginModal = () => (
    showLogin && (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-gray-800 p-8 rounded-lg max-w-md w-full mx-4">
          <h2 className="text-2xl font-bold text-white mb-4">Connexion Admin</h2>
          <div className="space-y-4">
            <input
              type="password"
              placeholder="Mot de passe"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              className="w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            />
            <div className="flex gap-4">
              <button
                onClick={handleLogin}
                className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-3 rounded-lg font-semibold text-white transition-colors"
              >
                Se connecter
              </button>
              <button
                onClick={() => setShowLogin(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 px-4 py-3 rounded-lg font-semibold text-white transition-colors"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  );

  useEffect(() => {
    if (isAdmin) {
      loadAnalytics();
    }
  }, [isAdmin]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navigation />
      {currentView === 'casino' && <CasinoView />}
      {currentView === 'calls' && <CallsView />}
      {currentView === 'admin' && isAdmin && <AdminView />}
      <LoginModal />
      
      {/* Footer */}
      <footer className="mt-16 text-center text-sm text-gray-400 hover:text-white transition-opacity opacity-70 px-4 py-6">
        <p>
          Développé avec ❤️ par <span className="text-purple-400 font-semibold">Browkse</span>
        </p>
        <p>
          📻 Suis <span className="text-white font-semibold">Skrymi</span> sur :
          <a href="https://dlive.tv/skrymi" className="text-blue-400 hover:underline mx-1" target="_blank" rel="noopener noreferrer">DLive</a>
          |
          <a href="https://kick.com/skrymi" className="text-green-400 hover:underline mx-1" target="_blank" rel="noopener noreferrer">Kick</a>
          |
          <a href="https://www.twitch.tv/skrymi" className="text-purple-400 hover:underline mx-1" target="_blank" rel="noopener noreferrer">Twitch</a>
          |
          <a href="https://www.youtube.com/@skrymi777" className="text-red-400 hover:underline mx-1" target="_blank" rel="noopener noreferrer">YouTube</a>
          |
          <a href="mailto:Browkse0@gmail.com" className="text-green-400 hover:underline mx-1" target="_blank" rel="noopener noreferrer">Dev : Browkse</a>
        </p>
        <p className="text-gray-500 text-xs mt-2">© 2025 Skrymi. Tous droits réservés.</p>
      </footer>
    </div>
  );
};

export default App;