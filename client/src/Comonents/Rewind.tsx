import React, { useState, useEffect } from "react";
import {
  ChakraProvider,
  Box,
  Input,
  Button,
  VStack,
  HStack,
  Text,
} from "@chakra-ui/react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

const App = () => {
  const [timestamp, setTimestamp] = useState("");
  const [message, setMessage] = useState("Message goes here");
  const [selectedDate, setSelectedDate] = useState(new Date());

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const momentParam = searchParams.get("moment");
    if (momentParam) {
      setTimestamp(momentParam);
      setSelectedDate(new Date(parseFloat(momentParam) * 1000));

      openRewindMoment(momentParam, true);
    }
  }, []);

  const openRewindMoment = (ts: string, forward: boolean | undefined) => {
    setMessage(`Open ${ts}`);
    const url = `rewindai://show-moment?timestamp=${ts}`;
    if (url.startsWith("rewindai://")) {
      if (forward) {
        let timeoutId = setTimeout(() => {
          setMessage("Timeout completed!");
          // You can call any function here
          window.close();
        }, 3000); // 3000 milliseconds = 3 seconds
      } else {
        window.open(url, "_blank");
      }
    }
  };

  const handleButtonClick = () => {
    openRewindMoment(timestamp,false);
  };

  const handleDateTimeChange = (date: Date | null) => {
    if (date) { // Check if date is not null
      setSelectedDate(date);
      setTimestamp((date.getTime() / 1000).toFixed(3));
    }
  };

  const handleTimestampChange = (e: { target: { value: any; }; }) => {
    const newTimestamp = e.target.value;
    setTimestamp(newTimestamp);
    const date = new Date(parseFloat(newTimestamp) * 1000);
    if (!isNaN(date.getTime())) {
      setSelectedDate(date);
    }
  };

  return (
    <ChakraProvider>
      STUasdasfasdf
      <Box p={4}>
        <VStack spacing={4} align="stretch">
          <HStack spacing={4}>
            <Box>
              <Text mb={2}>Date:</Text>
              <DatePicker
                selected={selectedDate}
                onChange={handleDateTimeChange}
                dateFormat="MMMM d, yyyy"
                customInput={<Input />}
              />
            </Box>
            <Box>
              <Text mb={2}>Time:</Text>
              <DatePicker
                selected={selectedDate}
                onChange={handleDateTimeChange}
                showTimeSelect
                showTimeSelectOnly
                timeIntervals={15}
                timeCaption="Time"
                dateFormat="h:mm aa"
                customInput={<Input />}
              />
            </Box>
          </HStack>
          <Box>
            <Text mb={2}>Timestamp:</Text>
            <Input
              value={timestamp}
              onChange={handleTimestampChange}
              placeholder="Enter timestamp"
            />
          </Box>
          <Button colorScheme="blue" onClick={handleButtonClick}>
            Moment {message}
          </Button>
        </VStack>
      </Box>
    </ChakraProvider>
  );
};
if (module.hot) {
  module.hot.accept('./Rewind', () => {
    // Callback function to handle module updates
  });
}
export default App;

