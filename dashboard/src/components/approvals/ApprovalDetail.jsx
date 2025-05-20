// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file creates a detailed view of something that needs to be approved.
// It shows all the information about the item and lets users approve or reject it.

// High School Explanation:
// This component displays detailed information about an approval request including
// its content, metadata, and history. It provides interfaces for reviewing, commenting on,
// and taking action (approve/reject) on the approval request with appropriate validations.

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApprovalStore } from '../../stores/approvalStore';
import { useNotificationContext } from '../components/shared/NotificationProvider';
import { formatDate } from '../../utils/formatters';
import { 
  RiCheckboxCircleLine, 
  RiCloseCircleLine,
  RiArrowLeftLine,
  RiTimeLine,
  RiUserLine,
  RiCalendarEventLine,
  RiFileTextLine,
  RiImageLine,
  RiMoneyDollarCircleLine,
  RiTargetLine
} from 'react-icons/ri';

// Component for displaying approval details
const ApprovalDetail = ({ approval, onClose }) => {
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { approveRequest, rejectRequest } = useApprovalStore();
  const { success, error } = useNotificationContext();
  const navigate = useNavigate();
  
  // If no approval is provided, show placeholder
  if (!approval) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          Select an approval request to view details
        </p>
      </div>
    );
  }
  
  // Handle approval submission
  const handleApprove = async () => {
    setIsSubmitting(true);
    
    try {
      await approveRequest(approval.id, feedback);
      success('Approval request approved successfully');
      
      if (onClose) {
        onClose();
      } else {
        navigate('/approvals');
      }
    } catch (err) {
      error('Failed to approve request: ' + (err.message || 'Unknown error'));
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Handle rejection submission
  const handleReject = async () => {
    if (!feedback.trim()) {
      error('Please provide feedback for rejection');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await rejectRequest(approval.id, feedback);
      success('Approval request rejected');
      
      if (onClose) {
        onClose();
      } else {
        navigate('/approvals');
      }
    } catch (err) {
      error('Failed to reject request: ' + (err.message || 'Unknown error'));
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Get icon based on approval type
  const getTypeIcon = () => {
    switch (approval.type) {
      case 'creative':
        return <RiImageLine className="w-5 h-5" />;
      case 'budget':
        return <RiMoneyDollarCircleLine className="w-5 h-5" />;
      case 'target':
        return <RiTargetLine className="w-5 h-5" />;
      case 'schedule':
        return <RiCalendarEventLine className="w-5 h-5" />;
      default:
        return <RiFileTextLine className="w-5 h-5" />;
    }
  };
  
  // Format the approval deadline
  const deadline = formatDate(approval.deadline);
  
  // Calculate time remaining
  const getTimeRemaining = () => {
    const now = new Date();
    const deadlineDate = new Date(approval.deadline);
    const diffMs = deadlineDate - now;
    
    // If deadline has passed
    if (diffMs <= 0) {
      return { text: 'Overdue', urgent: true };
    }
    
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    // Less than 24 hours
    if (diffHours < 24) {
      return { 
        text: diffHours === 0 ? 'Due today' : `${diffHours} hours remaining`, 
        urgent: diffHours < 12
      };
    }
    
    // Days remaining
    const diffDays = Math.floor(diffHours / 24);
    return { 
      text: `${diffDays} days remaining`, 
      urgent: false
    };
  };
  
  const timeRemaining = getTimeRemaining();
  const deadlineClasses = timeRemaining.urgent 
    ? 'text-red-600 dark:text-red-400 font-medium' 
    : 'text-gray-500 dark:text-gray-400';
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-4 sm:px-6">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
            {getTypeIcon()}
            <span className="ml-2">{approval.title}</span>
          </h2>
          
          {onClose && (
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400"
            >
              <RiArrowLeftLine className="w-5 h-5" />
              <span className="sr-only">Back</span>
            </button>
          )}
        </div>
      </div>
      
      {/* Content */}
      <div className="p-4 sm:p-6">
        {/* Meta information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <RiUserLine className="mr-1.5 h-4 w-4 flex-shrink-0" />
            <span>Requested by: <span className="font-medium">{approval.requestedBy}</span></span>
          </div>
          
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <RiCalendarEventLine className="mr-1.5 h-4 w-4 flex-shrink-0" />
            <span>Created: <span className="font-medium">{formatDate(approval.createdAt)}</span></span>
          </div>
          
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <RiTimeLine className="mr-1.5 h-4 w-4 flex-shrink-0" />
            <span>Deadline: <span className="font-medium">{deadline}</span></span>
          </div>
          
          <div className={`flex items-center text-sm ${deadlineClasses}`}>
            <RiTimeLine className="mr-1.5 h-4 w-4 flex-shrink-0" />
            <span>{timeRemaining.text}</span>
          </div>
        </div>
        
        {/* Campaign information */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Campaign</h3>
          <p className="text-base font-medium text-gray-900 dark:text-white">
            {approval.campaign}
          </p>
        </div>
        
        {/* Description */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Description</h3>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-4">
            <p className="text-base text-gray-900 dark:text-white whitespace-pre-wrap">
              {approval.description}
            </p>
          </div>
        </div>
        
        {/* Content preview based on type */}
        {approval.type === 'creative' && approval.preview && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Preview</h3>
            <div className="mt-2 bg-gray-100 dark:bg-gray-700 rounded-md p-4 flex justify-center">
              <img 
                src={approval.preview} 
                alt="Creative preview" 
                className="max-h-96 rounded-md"
              />
            </div>
          </div>
        )}
        
        {/* Feedback field */}
        <div className="mb-6">
          <label htmlFor="feedback" className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
            Feedback
          </label>
          <textarea 
            id="feedback" 
            rows={4} 
            className="w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary focus:ring-primary dark:bg-gray-700 dark:text-white"
            placeholder="Add your comments or feedback here..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {approval.type === 'creative' ? 'Provide feedback on the creative assets.' : 'Add any comments or feedback regarding this request.'}
          </p>
        </div>
        
        {/* Action buttons */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={handleReject}
            disabled={isSubmitting}
            className="inline-flex justify-center items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
          >
            <RiCloseCircleLine className="mr-1.5 h-5 w-5 text-red-500" />
            Reject
          </button>
          
          <button
            type="button"
            onClick={handleApprove}
            disabled={isSubmitting}
            className="inline-flex justify-center items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
          >
            <RiCheckboxCircleLine className="mr-1.5 h-5 w-5" />
            Approve
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApprovalDetail;