import React from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { AlertOctagon, Home } from 'lucide-react';
import { PageId } from '../components/layout/Sidebar';

interface NotFoundPageProps {
  onNavigate: (page: PageId) => void;
}

export const NotFoundPage: React.FC<NotFoundPageProps> = ({ onNavigate }) => {
  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <Card className="p-8 text-center max-w-md">
        <div className="p-3 rounded-full bg-rose-50 border border-rose-200 text-rose-600 inline-block mb-3">
          <AlertOctagon className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-1">404 Page Not Found</h2>
        <p className="text-xs text-slate-500 mb-5">
          The requested route or benchmark view does not exist in the navigation map.
        </p>
        <Button variant="primary" size="sm" onClick={() => onNavigate('dashboard')} icon={<Home className="w-4 h-4" />}>
          Return to Dashboard
        </Button>
      </Card>
    </div>
  );
};
