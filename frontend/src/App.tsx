import { useState } from 'react';
import { Sidebar, PageId } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';

// Pages
import { DashboardPage } from './pages/DashboardPage';
import { AIRecommendationPage } from './pages/AIRecommendationPage';
import { BenchmarkExplorerPage } from './pages/BenchmarkExplorerPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ProcessorsPage } from './pages/ProcessorsPage';
import { MLKEMVariantsPage } from './pages/MLKEMVariantsPage';
import { AboutPage } from './pages/AboutPage';
import { SettingsPage } from './pages/SettingsPage';
import { NotFoundPage } from './pages/NotFoundPage';

export function App() {
  const [activePage, setActivePage] = useState<PageId>('dashboard');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const handleNavigate = (page: PageId) => {
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderCurrentPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <DashboardPage onNavigate={handleNavigate} />;
      case 'recommendation':
        return <AIRecommendationPage />;
      case 'benchmarks':
        return <BenchmarkExplorerPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'processors':
        return <ProcessorsPage />;
      case 'variants':
        return <MLKEMVariantsPage />;
      case 'about':
        return <AboutPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <NotFoundPage onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-[#F7F4EE] text-slate-800 font-sans selection:bg-slate-200">
      {/* Left Sidebar */}
      <Sidebar
        activePage={activePage}
        onNavigate={handleNavigate}
        isOpen={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <Navbar
          activePage={activePage}
          onNavigate={handleNavigate}
          onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
        />

        {/* Page Body Viewport */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {renderCurrentPage()}
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}

export default App;
