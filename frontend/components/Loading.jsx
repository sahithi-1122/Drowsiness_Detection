/**
 * Loading indicator component
 */
export default function Loading({ message = "Processing..." }) {
  return (
    <div className="flex flex-col items-center justify-center space-y-4 py-8">
      <div className="relative">
        {/* Spinning circle */}
        <div className="w-16 h-16 border-4 border-blue-200 dark:border-blue-900 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
        
        {/* Inner pulsing circle */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-blue-500 rounded-full animate-pulse opacity-50"></div>
      </div>
      
      <p className="text-gray-600 dark:text-gray-400 text-sm font-medium animate-pulse">
        {message}
      </p>
    </div>
  );
}
