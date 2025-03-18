// React imports
import {
  Anchor,
  Box,
  Button,
  Checkbox,
  Grid,
  Group,
  Input,
  MantineProvider,
  Stack,
  Text,
  Textarea,
} from "@mantine/core";
import "@mantine/core/styles.css";
import { useForm } from "@mantine/form";
import { useEffect, useState } from "react";

// Import CSS
import "./App.css";

// Recursive component to render each group and command
const TreeNode = ({ node, level = 0, onCommandClick }) => (
  <Box pl={level * 16} className={level > 0 ? "tree-indent" : ""}>
    {node.is_group ? (
      <>
        <Text className="tree-group" mt={4} mb={4}>
          {node.name}
        </Text>
        <Stack spacing={0} gap="xs">
          {node.children.map((child, index) => (
            <TreeNode
              key={index}
              node={child}
              level={level + 1}
              onCommandClick={onCommandClick}
            />
          ))}
        </Stack>
      </>
    ) : (
      <Anchor
        href="#"
        className="tree-command"
        onClick={(e) => {
          e.preventDefault();
          onCommandClick(node);
        }}
      >
        <Text mt={2} mb={2}>
          {node.name}
        </Text>
      </Anchor>
    )}
  </Box>
);

const TreeView = ({ tree, onCommandClick }) => (
  <Box className="tree-view-container">
    <TreeNode node={tree} onCommandClick={onCommandClick} />
  </Box>
);

// Main component
const App = () => {
  const [tree, setTree] = useState({});
  const [selectedCommand, setSelectedCommand] = useState(null);
  const [commandOutput, setCommandOutput] = useState("");

  useEffect(() => {
    const treeElement = document.getElementById("tree");
    if (treeElement) {
      setTree(JSON.parse(treeElement.textContent));
    }
  }, []);

  const handleCommandClick = (command) => {
    setSelectedCommand(command);
    setCommandOutput("");
  };

  // Initialize form
  const form = useForm({
    initialValues: selectedCommand
      ? selectedCommand.inputs.reduce((values, input) => {
          values[input.name] = input.default || "";
          return values;
        }, {})
      : {},
  });

  const handleRunCommand = async (event) => {
    event.preventDefault(); // Prevent default form submission

    if (!selectedCommand) return;

    let inputs = { ...form.values };

    // Exclude `streaming=true` for non-streaming routes
    const isStreamingAllowed =
      !selectedCommand.endpoint.includes("/routes") &&
      !selectedCommand.endpoint.includes("/app_metadata");

    if (isStreamingAllowed) {
      inputs.streaming = true;
    }

    const queryString = new URLSearchParams(inputs).toString();

    const isGetRequest =
      selectedCommand.endpoint.includes("/routes") ||
      selectedCommand.endpoint.includes("/app_metadata");

    const url = isGetRequest
      ? `${selectedCommand.endpoint}?${queryString}`
      : selectedCommand.endpoint;

    console.log(
      `🔹 Sending ${isGetRequest ? "GET" : "POST"} request to: ${url}`
    );

    setCommandOutput(""); // Reset output

    try {
      const response = await fetch(url, {
        method: isGetRequest ? "GET" : "POST",
        headers: { "Content-Type": "application/json" },
        body: isGetRequest ? null : JSON.stringify(inputs),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      // Handle normal JSON response
      const rawText = await response.text();
      console.log("🔹 Raw response from server:", rawText);

      let parsedData;
      try {
        parsedData = JSON.parse(rawText); // Try parsing as JSON
      } catch (jsonError) {
        console.warn("⚠️ Server returned plain text instead of JSON.");
        parsedData = rawText; // Use raw text if JSON parsing fails
      }

      setCommandOutput(
        typeof parsedData === "object"
          ? JSON.stringify(parsedData, null, 2) // Pretty-print JSON
          : parsedData.toString()
      );
    } catch (error) {
      console.error("❌ Request failed:", error);
      setCommandOutput(`❌ Error: ${error.message}`);
    }
  };

  const handleReset = () => {
    if (selectedCommand) {
      form.reset();
      setCommandOutput("");
    }
  };

  return (
    <MantineProvider>
      <Grid grow>
        {/* Left Panel: Command Tree */}
        <Grid.Col span={4} className="grid-column">
          <Text
            size="xl"
            weight={700}
            mt={0}
            mb={12}
            className="tree-view-title"
          >
            Rescuebox CLI
          </Text>
          <TreeView tree={tree} onCommandClick={handleCommandClick} />
        </Grid.Col>

        {/* Right Panel: Command Details and Output */}
        <Grid.Col span={8} className="grid-column">
          {selectedCommand ? (
            <>
              <Group justify="space-between" mb={8}>
                <Text size="xl" weight={600}>
                  {selectedCommand.name}
                </Text>
                <Button variant="light" onClick={handleReset}>
                  Reset
                </Button>
              </Group>
              <Text mb={12} color="dimmed">
                {selectedCommand.help || "No description available."}
              </Text>

              {/* Command Form */}
              <form onSubmit={handleRunCommand} className="command-form">
                <Stack spacing="xs" mb={12}>
                  {selectedCommand.inputs.map((input) => (
                    <Box key={input.name}>
                      {input.help && (
                        <Text size="sm" color="dimmed" mb={4}>
                          {input.help}
                        </Text>
                      )}
                      {input.type === "str" && (
                        <Input
                          placeholder={input.default || ""}
                          {...form.getInputProps(input.name)}
                          required
                        />
                      )}
                      {input.type === "int" && (
                        <Input
                          type="number"
                          placeholder={input.default?.toString() || ""}
                          {...form.getInputProps(input.name)}
                          required
                        />
                      )}
                      {input.type === "bool" && (
                        <Checkbox
                          label={input.name}
                          {...form.getInputProps(input.name, {
                            type: "checkbox",
                          })}
                        />
                      )}
                    </Box>
                  ))}
                  <Button type="submit">Run Command</Button>
                </Stack>
              </form>

              {/* Command Output */}
              <Text mt={16} mb={4} weight={500}>
                Command Output:
              </Text>
              <Textarea
                value={commandOutput}
                readOnly
                minRows={10}
                className="command-output"
              />
            </>
          ) : (
            <Text>Select a command from the left panel to see details</Text>
          )}
        </Grid.Col>
      </Grid>
    </MantineProvider>
  );
};

export default App;
