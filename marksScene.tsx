import {Code, Rect, Txt, lines} from '@motion-canvas/2d';
import {all, createRef, makeScene2D, waitFor} from '@motion-canvas/core';

export default makeScene2D(function* (view) {
  const ideWindow = createRef<Rect>();
  const cameraLayer = createRef<Rect>();
  const code = createRef<Code>();
  const command = createRef<Txt>();
  const output = createRef<Txt>();

  const pythonCode = `# student_grades.py

students = {
    "Alice": [78, 82, 91],
    "Bob": [65, 70, 72],
    "Charlie": [90, 92, 88],
    "Diana": [55, 60, 58]
}

def calculate_average(scores):
    total = 0

    for score in scores:
        total += score

    return total / len(scores)


def assign_grade(avg):

    if avg >= 90:
        return "A"

    elif avg >= 80:
        return "B"

    elif avg >= 70:
        return "C"

    elif avg >= 60:
        return "D"

    else:
        return "F"


print("Student Results")
print("----------------")

for name, scores in students.items():

    average = calculate_average(scores)

    grade = assign_grade(average)

    print(f"{name} -> Avg: {average:.2f}, Grade: {grade}")`;

  const terminalOutput = `Student Results
----------------
Alice -> Avg: 83.67, Grade: B
Bob -> Avg: 69.00, Grade: D
Charlie -> Avg: 90.00, Grade: A
Diana -> Avg: 57.67, Grade: F`;

  view.add(
    <Rect width={1920} height={1080} fill={'#0d1117'}>
      <Rect
        ref={ideWindow}
        width={1680}
        height={920}
        radius={18}
        fill={'#161b22'}
        stroke={'#30363d'}
        lineWidth={2}
        shadowColor={'#00000088'}
        shadowBlur={24}
      >
        <Rect width={1680} height={58} y={-431} fill={'#21262d'} radius={[18, 18, 0, 0]}>
          <Txt
            text={'marks.py'}
            fill={'#c9d1d9'}
            fontFamily={'JetBrains Mono, monospace'}
            fontSize={26}
            x={-730}
          />
          <Rect x={-810} width={14} height={14} radius={7} fill={'#ff5f57'} />
          <Rect x={-784} width={14} height={14} radius={7} fill={'#febc2e'} />
          <Rect x={-758} width={14} height={14} radius={7} fill={'#28c840'} />
        </Rect>

        <Rect ref={cameraLayer} y={-110}>
          <Code
            ref={code}
            width={1600}
            height={610}
            language={'python'}
            fontFamily={'JetBrains Mono, monospace'}
            fontSize={32}
            lineHeight={48}
            code={''}
          />
        </Rect>

        <Rect width={1680} height={230} y={344} fill={'#0b0f14'} stroke={'#30363d'} lineWidth={1}>
          <Txt
            text={'TERMINAL'}
            fontFamily={'JetBrains Mono, monospace'}
            fontSize={22}
            fill={'#7d8590'}
            x={-760}
            y={-86}
          />
          <Txt
            ref={command}
            text={''}
            fontFamily={'JetBrains Mono, monospace'}
            fontSize={28}
            fill={'#58a6ff'}
            x={-620}
            y={-36}
            textAlign={'left'}
          />
          <Txt
            ref={output}
            text={''}
            fontFamily={'JetBrains Mono, monospace'}
            fontSize={24}
            lineHeight={36}
            fill={'#c9d1d9'}
            x={-620}
            y={48}
            textAlign={'left'}
          />
        </Rect>
      </Rect>
    </Rect>,
  );

  yield* code().code(pythonCode, 7.5);

  yield* all(cameraLayer().scale(1.08, 0.5), cameraLayer().position.y(-20, 0.5), code().selection(lines(3, 8), 0.5));
  yield* waitFor(1.1);

  yield* all(cameraLayer().scale(1.14, 0.5), cameraLayer().position.y(90, 0.5), code().selection(lines(10, 16), 0.5));
  yield* waitFor(1.1);

  yield* all(cameraLayer().scale(1.2, 0.5), cameraLayer().position.y(245, 0.5), code().selection(lines(19, 33), 0.5));
  yield* waitFor(1.2);

  yield* all(cameraLayer().scale(1.14, 0.5), cameraLayer().position.y(410, 0.5), code().selection(lines(36, 42), 0.5));
  yield* waitFor(1.2);

  yield* all(cameraLayer().scale(1, 0.5), cameraLayer().position.y(0, 0.5), code().selection(lines(1, 1), 0.4));

  yield* command().text('python marks.py', 1.2);
  yield* waitFor(0.4);
  yield* output().text(terminalOutput, 2.4);
  yield* waitFor(1.2);
});
